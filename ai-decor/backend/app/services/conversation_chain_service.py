"""ConversationChain service using Redis for automatic chat history storage."""

from typing import Optional
from langchain.memory import ConversationBufferMemory
from langchain_redis import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from app.core.config import settings
from app.core.logging import logger


class ConversationChainService:
    """Service for managing conversation chains with Redis-based memory."""
    
    def __init__(self):
        """Initialize the conversation chain service."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.DEFAULT_LLM_TEMPERATURE,
            api_key=settings.LLM_API_KEY,
            max_tokens=settings.MAX_TOKENS,
        )
        self._chains: dict[str, ConversationChain] = {}
    
    def get_or_create_chain(self, session_id: str) -> ConversationChain:
        """Get or create a conversation chain for a session.
        
        Args:
            session_id (str): The session ID for the conversation.
            
        Returns:
            ConversationChain: The conversation chain for the session.
        """
        if session_id not in self._chains:
            # Create Redis client manually to avoid parameter conflicts
            import redis
            redis_url = settings.REDIS_URL
            if settings.REDIS_PASSWORD:
                redis_url = redis_url.replace("redis://", f"redis://:{settings.REDIS_PASSWORD}@")
            
            redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Create Redis chat history for this session (Redis Stack optimized)
            chat_history = RedisChatMessageHistory(
                session_id=session_id,
                redis_client=redis_client,
                ttl=settings.CHAT_HISTORY_TTL,  # Messages expire after TTL
                key_prefix="interior_design:",  # Namespace for our app
            )
            
            # Create memory with Redis chat history
            memory = ConversationBufferMemory(
                chat_memory=chat_history,
                return_messages=True,  # Return messages for context
                memory_key="chat_history",  # Key for memory in chain
            )
            
            # Create conversation chain with memory
            chain = ConversationChain(
                llm=self.llm,
                memory=memory,
                verbose=True,  # Enable verbose logging
            )
            
            self._chains[session_id] = chain
            logger.info("conversation_chain_created", session_id=session_id)
        
        return self._chains[session_id]
    
    async def get_response(self, session_id: str, user_input: str) -> str:
        """Get a response from the conversation chain.
        
        Args:
            session_id (str): The session ID.
            user_input (str): The user's input message.
            
        Returns:
            str: The AI's response.
        """
        try:
            chain = self.get_or_create_chain(session_id)
            
            # The chain automatically:
            # 1. Loads previous messages from Redis
            # 2. Adds user input to memory
            # 3. Generates AI response
            # 4. Saves both user input and AI response to Redis
            response = await chain.ainvoke({"input": user_input})
            
            logger.info("conversation_response_generated", session_id=session_id)
            return response["response"]
            
        except Exception as e:
            logger.error("conversation_response_failed", session_id=session_id, error=str(e))
            raise e
    
    async def get_chat_history(self, session_id: str) -> list[dict]:
        """Get chat history for a session.
        
        Args:
            session_id (str): The session ID.
            
        Returns:
            list[dict]: List of messages in the conversation.
        """
        try:
            chain = self.get_or_create_chain(session_id)
            
            # Get messages from memory
            messages = chain.memory.chat_memory.messages
            
            # Convert to dict format
            history = []
            for message in messages:
                history.append({
                    "role": message.__class__.__name__.lower().replace("message", ""),
                    "content": message.content
                })
            
            logger.info("chat_history_retrieved", session_id=session_id, message_count=len(history))
            return history
            
        except Exception as e:
            logger.error("get_chat_history_failed", session_id=session_id, error=str(e))
            return []
    
    async def clear_chat_history(self, session_id: str) -> None:
        """Clear chat history for a session.
        
        Args:
            session_id (str): The session ID.
        """
        try:
            if session_id in self._chains:
                # Clear the memory
                self._chains[session_id].memory.clear()
                
                # Remove from chains dict
                del self._chains[session_id]
                
            logger.info("chat_history_cleared", session_id=session_id)
            
        except Exception as e:
            logger.error("clear_chat_history_failed", session_id=session_id, error=str(e))
            raise e
    
    def remove_chain(self, session_id: str) -> None:
        """Remove a conversation chain from memory.
        
        Args:
            session_id (str): The session ID.
        """
        if session_id in self._chains:
            del self._chains[session_id]
            logger.info("conversation_chain_removed", session_id=session_id)


# Global instance
conversation_service = ConversationChainService()
