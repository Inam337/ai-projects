"""Simplified Redis service that definitely works."""

import redis.asyncio as redis
from typing import List
from app.core.config import settings
from app.core.logging import logger
from app.schemas import Message


class SimpleRedisService:
    """Simplified Redis service for chat history."""
    
    def __init__(self):
        """Initialize the Redis service."""
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to Redis."""
        try:
            key = f"interior_design:chat:{session_id}"
            # Store as JSON string
            import json
            message_data = {
                "role": message.role,
                "content": message.content,
                "timestamp": message.created_at if hasattr(message, 'created_at') else None
            }
            
            # Add to list
            await self.redis_client.lpush(key, json.dumps(message_data))
            # Set TTL
            await self.redis_client.expire(key, settings.CHAT_HISTORY_TTL)
            
            logger.info("message_added_to_redis", session_id=session_id, role=message.role)
            
        except Exception as e:
            logger.error("add_message_failed", session_id=session_id, error=str(e))
            raise e
    
    async def get_messages(self, session_id: str) -> List[Message]:
        """Get messages from Redis."""
        try:
            key = f"interior_design:chat:{session_id}"
            messages_data = await self.redis_client.lrange(key, 0, -1)
            
            messages = []
            for msg_data in reversed(messages_data):  # Reverse to get chronological order
                import json
                data = json.loads(msg_data)
                messages.append(Message(
                    role=data["role"],
                    content=data["content"]
                ))
            
            logger.info("messages_retrieved_from_redis", session_id=session_id, count=len(messages))
            return messages
            
        except Exception as e:
            logger.error("get_messages_failed", session_id=session_id, error=str(e))
            return []
    
    async def clear_messages(self, session_id: str) -> None:
        """Clear messages from Redis."""
        try:
            key = f"interior_design:chat:{session_id}"
            await self.redis_client.delete(key)
            logger.info("messages_cleared_from_redis", session_id=session_id)
            
        except Exception as e:
            logger.error("clear_messages_failed", session_id=session_id, error=str(e))
            raise e
    
    async def test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            result = await self.redis_client.ping()
            logger.info("redis_connection_test", result=result)
            return result
        except Exception as e:
            logger.error("redis_connection_test_failed", error=str(e))
            return False
    
    async def debug_session(self, session_id: str) -> dict:
        """Debug session data in Redis."""
        try:
            key = f"interior_design:chat:{session_id}"
            exists = await self.redis_client.exists(key)
            length = await self.redis_client.llen(key) if exists else 0
            ttl = await self.redis_client.ttl(key) if exists else -1
            
            debug_info = {
                "session_id": session_id,
                "key": key,
                "exists": bool(exists),
                "length": length,
                "ttl": ttl
            }
            
            logger.info("redis_session_debug", **debug_info)
            return debug_info
            
        except Exception as e:
            logger.error("redis_session_debug_failed", session_id=session_id, error=str(e))
            return {"error": str(e)}


# Global instance
simple_redis_service = SimpleRedisService()
