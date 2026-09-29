"""Chatbot API endpoints for handling chat interactions.

This module provides endpoints for chat interactions, including regular chat,
streaming chat, message history management, and chat history clearing.
"""

import json
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from fastapi.responses import StreamingResponse
from app.core.metrics import llm_stream_duration_seconds
from app.api.v1.auth import get_current_session
from app.core.config import settings
from app.core.langgraph.graph import LangGraphAgent
from app.core.limiter import limiter
from app.core.logging import logger
from app.models.session import Session
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Message,
    StreamResponse,
)
from app.services.conversation_chain_service import conversation_service

router = APIRouter()
agent = LangGraphAgent()



@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["chat"][0])
async def chat(
    request: Request,
    chat_request: ChatRequest,
    session: Session = Depends(get_current_session),
):
    """Process a chat request and return only the new AI response.

    This endpoint is optimized for ongoing conversation. It processes the user's
    message and returns ONLY the new AI response, not the full conversation history.

    Args:
        request: The FastAPI request object for rate limiting.
        chat_request: The chat request containing the new user message.
        session: The current session from the auth token.

    Returns:
        ChatResponse: Only the new AI response message.

    Raises:
        HTTPException: If there's an error processing the request.
    """
    try:
        logger.info(
            "chat_request_received",
            session_id=session.id,
            message_count=len(chat_request.messages),
        )

        # Process the new message and get only the new AI response
        result = await agent.get_response(
            chat_request.messages, session.id, user_id=session.user_id
        )
        
        logger.info("chat_request_processed", session_id=session.id, new_messages=len(result))

        # Return only the new AI response (not full conversation)
        return ChatResponse(messages=result)
    except Exception as e:
        logger.error("chat_request_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["chat_stream"][0])
async def chat_stream(
    request: Request,
    chat_request: ChatRequest,
    session: Session = Depends(get_current_session),
):
    """Process a chat request using LangGraph with streaming response.

    Args:
        request: The FastAPI request object for rate limiting.
        chat_request: The chat request containing messages.
        session: The current session from the auth token.

    Returns:
        StreamingResponse: A streaming response of the chat completion.

    Raises:
        HTTPException: If there's an error processing the request.
    """
    try:
        logger.info(
            "stream_chat_request_received",
            session_id=session.id,
            message_count=len(chat_request.messages),
        )

        async def event_generator():
            """Generate streaming events.

            Yields:
                str: Server-sent events in JSON format.

            Raises:
                Exception: If there's an error during streaming.
            """
            try:
                full_response = ""
                with llm_stream_duration_seconds.labels(model=agent.llm.model_name).time():
                    async for chunk in agent.get_stream_response(
                        chat_request.messages, session.id, user_id=session.user_id
                     ):
                        full_response += chunk
                        response = StreamResponse(content=chunk, done=False)
                        yield f"data: {json.dumps(response.model_dump())}\n\n"

                # Send final message indicating completion
                final_response = StreamResponse(content="", done=True)
                yield f"data: {json.dumps(final_response.model_dump())}\n\n"

            except Exception as e:
                logger.error(
                    "stream_chat_request_failed",
                    session_id=session.id,
                    error=str(e),
                    exc_info=True,
                )
                error_response = StreamResponse(content=str(e), done=True)
                yield f"data: {json.dumps(error_response.model_dump())}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.error(
            "stream_chat_request_failed",
            session_id=session.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["messages"][0])
async def get_session_messages(
    request: Request,
    session: Session = Depends(get_current_session),
):
    """Get all messages for a session.

    Args:
        request: The FastAPI request object for rate limiting.
        session: The current session from the auth token.

    Returns:
        ChatResponse: All messages in the session.

    Raises:
        HTTPException: If there's an error retrieving the messages.
    """
    try:
        messages = await agent.get_chat_history(session.id)
        logger.info("session_messages_loaded", session_id=session.id, message_count=len(messages))
        return ChatResponse(messages=messages)
    except Exception as e:
        logger.error("get_messages_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/context", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["messages"][0])
async def get_session_context(
    request: Request,
    session: Session = Depends(get_current_session),
):
    """Get full session context including complete chat history.

    This endpoint is specifically designed for loading session context
    when a user opens an existing session. Returns the ENTIRE conversation.

    Args:
        request: The FastAPI request object for rate limiting.
        session: The current session from the auth token.

    Returns:
        ChatResponse: Complete session context with all messages.

    Raises:
        HTTPException: If there's an error retrieving the session context.
    """
    try:
        # Load complete chat history from Redis
        messages = await agent.get_chat_history(session.id)
        
        # Add session metadata as a system message if there are existing messages
        if messages:
            # Add a welcome back message
            welcome_message = {
                "role": "system",
                "content": f"Welcome back to your design session '{session.name}'! You have {len(messages)} previous messages in this conversation."
            }
            # Insert at the beginning
            messages.insert(0, welcome_message)
        
        logger.info("session_context_loaded", 
                   session_id=session.id, 
                   session_name=session.name,
                   message_count=len(messages))
        
        return ChatResponse(messages=messages)
    except Exception as e:
        logger.error("get_session_context_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/redis/{session_id}")
async def debug_redis_session(session_id: str):
    """Debug Redis session data."""
    try:
        from app.services.simple_redis_service import simple_redis_service
        
        # Test connection
        connection_ok = await simple_redis_service.test_connection()
        
        # Debug session
        debug_info = await simple_redis_service.debug_session(session_id)
        
        # Try to get messages
        messages = await simple_redis_service.get_messages(session_id)
        
        return {
            "connection_ok": connection_ok,
            "debug_info": debug_info,
            "messages_count": len(messages),
            "messages": messages
        }
    except Exception as e:
        logger.error("debug_redis_failed", session_id=session_id, error=str(e))
        return {"error": str(e)}


@router.delete("/messages")
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["messages"][0])
async def clear_chat_history(
    request: Request,
    session: Session = Depends(get_current_session),
):
    """Clear all messages for a session.

    Args:
        request: The FastAPI request object for rate limiting.
        session: The current session from the auth token.

    Returns:
        dict: A message indicating the chat history was cleared.
    """
    try:
        await agent.clear_chat_history(session.id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        logger.error("clear_chat_history_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/conversation", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["chat"][0])
async def chat_with_conversation_chain(
    request: Request,
    chat_request: ChatRequest,
    session: Session = Depends(get_current_session),
):
    """Process a chat request using ConversationChain with automatic Redis storage.

    Args:
        request: The FastAPI request object for rate limiting.
        chat_request: The chat request containing messages.
        session: The current session from the auth token.

    Returns:
        ChatResponse: The processed chat response.

    Raises:
        HTTPException: If there's an error processing the request.
    """
    try:
        logger.info(
            "conversation_chat_request_received",
            session_id=session.id,
            message_count=len(chat_request.messages),
        )

        # Get the last user message (most recent input)
        if not chat_request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        last_message = chat_request.messages[-1]
        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # Use ConversationChain - automatically stores in Redis
        response_text = await conversation_service.get_response(
            session.id, 
            last_message.content
        )
        
        # Get updated chat history from Redis
        chat_history = await conversation_service.get_chat_history(session.id)
        
        logger.info("conversation_chat_request_processed", session_id=session.id)
        
        return ChatResponse(messages=chat_history)
        
    except Exception as e:
        logger.error("conversation_chat_request_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/conversation", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["messages"][0])
async def get_conversation_history(
    request: Request,
    session: Session = Depends(get_current_session),
):
    """Get conversation history from Redis using ConversationChain.

    Args:
        request: The FastAPI request object for rate limiting.
        session: The current session from the auth token.

    Returns:
        ChatResponse: All messages in the conversation.
    """
    try:
        messages = await conversation_service.get_chat_history(session.id)
        return ChatResponse(messages=messages)
    except Exception as e:
        logger.error("get_conversation_history_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/conversation")
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["messages"][0])
async def clear_conversation_history(
    request: Request,
    session: Session = Depends(get_current_session),
):
    """Clear conversation history from Redis.

    Args:
        request: The FastAPI request object for rate limiting.
        session: The current session from the auth token.

    Returns:
        dict: A message indicating the conversation history was cleared.
    """
    try:
        await conversation_service.clear_chat_history(session.id)
        return {"message": "Conversation history cleared successfully"}
    except Exception as e:
        logger.error("clear_conversation_history_failed", session_id=session.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
