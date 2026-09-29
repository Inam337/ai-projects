# 🗣️ ConversationChain + Redis Guide

This guide explains how to use the new ConversationChain endpoints that automatically store chat history in Redis.

## 🎯 **What is ConversationChain?**

ConversationChain is a LangChain component that:
- ✅ **Automatically stores** all messages in Redis
- ✅ **Loads conversation context** automatically
- ✅ **Manages session isolation** (each session has separate history)
- ✅ **Supports TTL** (messages expire after specified time)
- ✅ **No manual message management** needed

## 🚀 **New API Endpoints**

### 1. **Chat with Automatic Storage**
```http
POST /api/v1/chatbot/chat/conversation
```

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hi! I need help with my living room design."
    }
  ]
}
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hi! I need help with my living room design."
    },
    {
      "role": "assistant", 
      "content": "Hello! I'd be happy to help you design your living room..."
    }
  ]
}
```

### 2. **Get Conversation History**
```http
GET /api/v1/chatbot/messages/conversation
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hi! I need help with my living room design."
    },
    {
      "role": "assistant",
      "content": "Hello! I'd be happy to help you design your living room..."
    },
    {
      "role": "user", 
      "content": "My room is 12x15 feet. What furniture should I get?"
    },
    {
      "role": "assistant",
      "content": "For a 12x15 foot living room, I recommend..."
    }
  ]
}
```

### 3. **Clear Conversation History**
```http
DELETE /api/v1/chatbot/messages/conversation
```

**Response:**
```json
{
  "message": "Conversation history cleared successfully"
}
```

## 🔧 **How It Works**

### **Automatic Storage Flow:**
1. **User sends message** → API receives it
2. **ConversationChain loads** previous messages from Redis
3. **AI generates response** with full context
4. **Both user message and AI response** are automatically saved to Redis
5. **Next message** will have full conversation context

### **Session Isolation:**
- Each session ID gets its own Redis namespace
- Sessions are completely separate
- No cross-contamination between users

### **TTL (Time To Live):**
- Messages expire after `CHAT_HISTORY_TTL` seconds (default: 24 hours)
- Configurable via environment variable
- Set to 0 for no expiration

## 🛠️ **Setup Instructions**

### **1. Install Dependencies**
```bash
# Dependencies are already added to pyproject.toml
pip install langchain-redis redis
```

### **2. Start Redis**
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using Docker Compose
docker-compose up redis

# Or install locally
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu
```

### **3. Configure Environment**
```bash
# Add to your .env file
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=  # Optional
CHAT_HISTORY_TTL=86400  # 24 hours in seconds
```

### **4. Test the Setup**
```bash
# Run the test script
python test_conversation_chain.py
```

## 📊 **Comparison: LangGraph vs ConversationChain**

| Feature | LangGraph | ConversationChain |
|---------|-----------|-------------------|
| **Storage** | PostgreSQL + Manual | Redis + Automatic |
| **Context** | Manual management | Automatic loading |
| **Session Isolation** | Manual | Automatic |
| **TTL Support** | No | Yes |
| **Complexity** | High | Low |
| **Performance** | Good | Excellent |
| **Use Case** | Complex workflows | Simple conversations |

## 🎨 **Frontend Integration**

### **Update your frontend API calls:**

```typescript
// Instead of /chatbot/chat, use:
const response = await api.post('/chatbot/chat/conversation', {
  messages: [{ role: 'user', content: userMessage }]
});

// Get history:
const history = await api.get('/chatbot/messages/conversation');

// Clear history:
await api.delete('/chatbot/messages/conversation');
```

## 🔍 **Monitoring & Debugging**

### **Check Redis Storage:**
```bash
# Connect to Redis CLI
redis-cli

# List all keys
KEYS *

# Check specific session
GET "langchain:message_store:session-123"

# Monitor Redis activity
MONITOR
```

### **Logs:**
- All operations are logged with session IDs
- Check logs for Redis connection issues
- Monitor TTL expiration

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Redis Connection Failed**
   ```bash
   # Check if Redis is running
   redis-cli ping
   # Should return: PONG
   ```

2. **Messages Not Persisting**
   - Check Redis URL configuration
   - Verify session IDs are consistent
   - Check TTL settings

3. **Context Not Loading**
   - Ensure session ID is the same
   - Check if messages expired (TTL)
   - Verify Redis connection

## 🎯 **Best Practices**

1. **Use consistent session IDs** - Don't change them mid-conversation
2. **Set appropriate TTL** - Balance storage vs. performance
3. **Monitor Redis memory** - Set up alerts for high usage
4. **Handle Redis failures** - Implement fallback mechanisms
5. **Test thoroughly** - Verify session isolation works

## 🚀 **Next Steps**

1. **Update frontend** to use new endpoints
2. **Test with multiple sessions** to verify isolation
3. **Monitor Redis performance** in production
4. **Set up Redis monitoring** and alerts
5. **Consider Redis clustering** for high availability

---

**🎉 You now have automatic Redis-based chat history storage!** 

No more manual message management - just send messages and everything is handled automatically! 🚀
