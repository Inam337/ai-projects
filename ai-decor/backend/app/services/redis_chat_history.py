"""Redis-based chat history service for storing and retrieving conversation history."""

from typing import List, Optional
import redis.asyncio as redis
from langchain_redis import RedisChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.core.config import settings
from app.core.logging import logger
from app.schemas import Message


class RedisChatHistoryService:
    """Service for managing chat history using Redis."""
    
    def __init__(self):
        """Initialize the Redis chat history service."""
        self.redis_client: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
    
    def _get_redis_url(self) -> str:
        """Get Redis URL with password if provided.
        
        Returns:
            str: Redis URL with authentication if password is set.
        """
        if settings.REDIS_PASSWORD:
            return settings.REDIS_URL.replace("redis://", f"redis://:{settings.REDIS_PASSWORD}@")
        return settings.REDIS_URL
    
    def _create_chat_history(self, session_id: str) -> RedisChatMessageHistory:
        """Create a RedisChatMessageHistory instance.
        
        Args:
            session_id (str): The session ID.
            
        Returns:
            RedisChatMessageHistory: Configured chat history instance.
        """
        # Create Redis client manually to avoid parameter conflicts
        redis_client = redis.from_url(
            self._get_redis_url(),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Create RedisChatMessageHistory with the client
        return RedisChatMessageHistory(
            session_id=session_id,
            redis_client=redis_client,
            ttl=settings.CHAT_HISTORY_TTL,
            key_prefix="interior_design:"
        )
    
    async def _get_redis_client(self) -> redis.Redis:
        """Get or create a Redis client connection.
        
        Returns:
            redis.Redis: Redis client instance.
        """
        if self.redis_client is None:
            try:
                # Create connection pool with Redis Stack optimized settings
                self._connection_pool = redis.ConnectionPool.from_url(
                    self._get_redis_url(),
                    decode_responses=True,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                
                self.redis_client = redis.Redis(connection_pool=self._connection_pool)
                
                # Test connection
                await self.redis_client.ping()
                logger.info("redis_connected", url=settings.REDIS_URL)
                
            except Exception as e:
                logger.error("redis_connection_failed", error=str(e), url=settings.REDIS_URL)
                raise e
        
        return self.redis_client
    
    async def get_chat_history(self, session_id: str) -> List[Message]:
        """Get chat history for a session.
        
        Args:
            session_id (str): The session ID.
            
        Returns:
            List[Message]: List of messages in the chat history.
        """
        try:
            chat_history = self._create_chat_history(session_id)
            
            messages = await chat_history.aget_messages()
            
            # Convert LangChain messages to our Message schema
            result = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    result.append(Message(role="user", content=message.content))
                elif isinstance(message, AIMessage):
                    result.append(Message(role="assistant", content=message.content))
            
            logger.info("chat_history_retrieved", session_id=session_id, message_count=len(result))
            return result
            
        except Exception as e:
            logger.error("get_chat_history_failed", session_id=session_id, error=str(e))
            return []
    
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to the chat history.
        
        Args:
            session_id (str): The session ID.
            message (Message): The message to add.
        """
        try:
            chat_history = self._create_chat_history(session_id)
            
            if message.role == "user":
                await chat_history.aadd_user_message(message.content)
            elif message.role == "assistant":
                await chat_history.aadd_ai_message(message.content)
            
            logger.info("message_added", session_id=session_id, role=message.role)
            
        except Exception as e:
            logger.error("add_message_failed", session_id=session_id, error=str(e))
            raise e
    
    async def add_messages(self, session_id: str, messages: List[Message]) -> None:
        """Add multiple messages to the chat history.
        
        Args:
            session_id (str): The session ID.
            messages (List[Message]): The messages to add.
        """
        try:
            chat_history = self._create_chat_history(session_id)
            
            for message in messages:
                if message.role == "user":
                    await chat_history.aadd_user_message(message.content)
                elif message.role == "assistant":
                    await chat_history.aadd_ai_message(message.content)
            
            logger.info("messages_added", session_id=session_id, message_count=len(messages))
            
        except Exception as e:
            logger.error("add_messages_failed", session_id=session_id, error=str(e))
            raise e
    
    async def clear_chat_history(self, session_id: str) -> None:
        """Clear all chat history for a session.
        
        Args:
            session_id (str): The session ID.
        """
        try:
            chat_history = self._create_chat_history(session_id)
            
            await chat_history.aclear()
            logger.info("chat_history_cleared", session_id=session_id)
            
        except Exception as e:
            logger.error("clear_chat_history_failed", session_id=session_id, error=str(e))
            raise e
    
    async def get_all_messages(self, session_id: str) -> List[BaseMessage]:
        """Get all messages as LangChain BaseMessage objects.
        
        Args:
            session_id (str): The session ID.
            
        Returns:
            List[BaseMessage]: List of LangChain messages.
        """
        try:
            chat_history = self._create_chat_history(session_id)
            
            messages = await chat_history.aget_messages()
            logger.info("all_messages_retrieved", session_id=session_id, message_count=len(messages))
            return messages
            
        except Exception as e:
            logger.error("get_all_messages_failed", session_id=session_id, error=str(e))
            return []
    
    async def close(self) -> None:
        """Close the Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None


# Global instance
redis_chat_service = RedisChatHistoryService()
