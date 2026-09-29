#!/usr/bin/env python3
"""Simple Redis connection test."""

import redis
from langchain_redis import RedisChatMessageHistory

def test_redis_connection():
    """Test Redis connection and RedisChatMessageHistory."""
    
    print("🧪 Testing Redis connection...")
    
    # Test 1: Basic Redis connection
    try:
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        result = r.ping()
        print(f"✅ Basic Redis connection: {result}")
    except Exception as e:
        print(f"❌ Basic Redis connection failed: {e}")
        return False
    
    # Test 2: RedisChatMessageHistory with manual client
    try:
        redis_client = redis.from_url(
            "redis://localhost:6379/0",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        chat_history = RedisChatMessageHistory(
            session_id="test-session",
            redis_client=redis_client,
            ttl=86400,
            key_prefix="test:"
        )
        
        print("✅ RedisChatMessageHistory created successfully")
        
        # Test adding a message
        import asyncio
        async def test_message():
            await chat_history.aadd_user_message("Hello Redis!")
            messages = await chat_history.aget_messages()
            print(f"✅ Message added and retrieved: {len(messages)} messages")
            return True
        
        result = asyncio.run(test_message())
        return result
        
    except Exception as e:
        print(f"❌ RedisChatMessageHistory failed: {e}")
        return False

if __name__ == "__main__":
    success = test_redis_connection()
    if success:
        print("🎉 All Redis tests passed!")
    else:
        print("💥 Redis tests failed!")
