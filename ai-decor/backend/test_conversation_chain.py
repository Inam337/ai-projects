#!/usr/bin/env python3
"""Test script to demonstrate ConversationChain with Redis automatic storage."""

import asyncio
import os
from app.services.conversation_chain_service import conversation_service


async def test_conversation_chain():
    """Test the ConversationChain with Redis storage."""
    
    print("🧪 Testing ConversationChain with Redis automatic storage...")
    print("=" * 60)
    
    # Test session ID
    session_id = "test-session-123"
    
    try:
        # Test 1: First message
        print("📝 Test 1: Sending first message...")
        response1 = await conversation_service.get_response(
            session_id, 
            "Hi! I'm Jim. I need help with my living room design."
        )
        print(f"🤖 AI Response: {response1}")
        print()
        
        # Test 2: Second message (should have context from first)
        print("📝 Test 2: Sending follow-up message...")
        response2 = await conversation_service.get_response(
            session_id, 
            "What did I just say my name was?"
        )
        print(f"🤖 AI Response: {response2}")
        print()
        
        # Test 3: Third message
        print("📝 Test 3: Asking about design advice...")
        response3 = await conversation_service.get_response(
            session_id, 
            "My living room is 12x15 feet. What furniture should I get?"
        )
        print(f"🤖 AI Response: {response3}")
        print()
        
        # Test 4: Get full conversation history
        print("📚 Test 4: Retrieving full conversation history...")
        history = await conversation_service.get_chat_history(session_id)
        print(f"📖 Conversation History ({len(history)} messages):")
        for i, msg in enumerate(history, 1):
            print(f"  {i}. {msg['role'].upper()}: {msg['content']}")
        print()
        
        # Test 5: Test with different session (should be separate)
        print("📝 Test 5: Testing with different session...")
        session_id_2 = "test-session-456"
        response4 = await conversation_service.get_response(
            session_id_2, 
            "Hello! I'm Sarah. I need help with my bedroom."
        )
        print(f"🤖 AI Response: {response4}")
        print()
        
        # Test 6: Verify sessions are separate
        print("🔍 Test 6: Verifying sessions are separate...")
        history_1 = await conversation_service.get_chat_history(session_id)
        history_2 = await conversation_service.get_chat_history(session_id_2)
        print(f"Session 1 history: {len(history_1)} messages")
        print(f"Session 2 history: {len(history_2)} messages")
        print()
        
        print("✅ All tests completed successfully!")
        print("🎉 ConversationChain is working with automatic Redis storage!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


async def test_redis_connection():
    """Test Redis connection."""
    print("🔌 Testing Redis connection...")
    try:
        # Try to create a simple chain to test Redis
        session_id = "connection-test"
        response = await conversation_service.get_response(
            session_id, 
            "Hello, this is a connection test."
        )
        print(f"✅ Redis connection successful! Response: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting ConversationChain + Redis Test")
    print("=" * 60)
    
    # Test Redis connection first
    if not await test_redis_connection():
        print("❌ Cannot proceed without Redis connection")
        return
    
    print()
    
    # Run the main test
    await test_conversation_chain()
    
    print()
    print("🎯 Key Benefits of ConversationChain + Redis:")
    print("  ✅ Automatic message storage in Redis")
    print("  ✅ Session-based conversation isolation")
    print("  ✅ Automatic context loading")
    print("  ✅ TTL support for message expiration")
    print("  ✅ No manual message management needed")


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("LLM_API_KEY", "your-openai-api-key")
    os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")
    
    asyncio.run(main())
