# 🚀 Redis Stack Setup Guide

## 🐳 **Your Redis Stack Setup**

You're running Redis Stack with:
```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

This gives you:
- **Redis Server** on port `6379`
- **RedisInsight** (Web UI) on port `8001`
- **Redis Stack** with additional modules (JSON, Search, etc.)

## 🔧 **Environment Variables**

Add these to your `.env` file:

```bash
# Redis Configuration (Redis Stack)
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD=""
REDIS_DB="0"
REDIS_URL="redis://localhost:6379/0"
CHAT_HISTORY_TTL="86400"  # 24 hours in seconds
```

## 🎯 **Redis Stack Benefits**

### **1. RedisInsight Web UI**
- **URL**: http://localhost:8001
- **Features**: 
  - Visual data browser
  - Query editor
  - Memory usage monitoring
  - Key expiration tracking

### **2. Enhanced Redis Features**
- **JSON Support**: Store structured data
- **Search**: Full-text search capabilities
- **Time Series**: Time-based data storage
- **Graph**: Graph database functionality

## 🧪 **Test Your Setup**

### **1. Test Redis Connection**
```bash
# Test basic connection
redis-cli ping
# Should return: PONG

# Test with specific database
redis-cli -n 0 ping
```

### **2. Test with Python**
```python
import redis

# Test connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
print(r.ping())  # Should return: True

# Test basic operations
r.set('test_key', 'Hello Redis Stack!')
print(r.get('test_key'))  # Should return: Hello Redis Stack!
```

### **3. Test ConversationChain**
```bash
# Run the test script
python test_conversation_chain.py
```

## 📊 **Monitor Your Redis**

### **1. RedisInsight Dashboard**
- Open: http://localhost:8001
- Connect to: `localhost:6379`
- Database: `0`
- No password required

### **2. Command Line Monitoring**
```bash
# Monitor all Redis commands
redis-cli monitor

# Check memory usage
redis-cli info memory

# List all keys
redis-cli keys "*"

# Check specific session
redis-cli keys "*session-123*"
```

## 🔍 **Debugging Chat History**

### **1. Check Stored Messages**
```bash
# List all conversation keys
redis-cli keys "*langchain*"

# Check specific session
redis-cli keys "*session-123*"

# Get message content
redis-cli get "langchain:message_store:session-123"
```

### **2. Monitor TTL**
```bash
# Check TTL for a key
redis-cli ttl "langchain:message_store:session-123"

# -1 = no expiration
# -2 = key doesn't exist
# >0 = seconds until expiration
```

## 🚀 **Production Considerations**

### **1. Redis Persistence**
Your Redis Stack setup includes:
- **RDB snapshots** (default)
- **AOF logging** (optional)
- **Memory optimization**

### **2. Memory Management**
```bash
# Check memory usage
redis-cli info memory

# Set max memory (optional)
redis-cli config set maxmemory 512mb
redis-cli config set maxmemory-policy allkeys-lru
```

### **3. Security (Production)**
```bash
# Set password
redis-cli config set requirepass "your-secure-password"

# Update environment
REDIS_PASSWORD="your-secure-password"
REDIS_URL="redis://:your-secure-password@localhost:6379/0"
```

## 🎯 **Quick Start Commands**

### **1. Start Redis Stack**
```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### **2. Test Connection**
```bash
redis-cli ping
```

### **3. Open RedisInsight**
- Go to: http://localhost:8001
- Connect to: `localhost:6379`

### **4. Run Your App**
```bash
# Set environment variables
export REDIS_URL="redis://localhost:6379/0"
export LLM_API_KEY="your-openai-api-key"

# Start your FastAPI app
python -m uvicorn app.main:app --reload
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Connection Refused**
   ```bash
   # Check if Redis is running
   docker ps | grep redis-stack
   
   # Check logs
   docker logs redis-stack
   ```

2. **Port Already in Use**
   ```bash
   # Stop existing Redis
   docker stop redis-stack
   docker rm redis-stack
   
   # Start fresh
   docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
   ```

3. **Memory Issues**
   ```bash
   # Check Redis memory
   redis-cli info memory
   
   # Clear all data (careful!)
   redis-cli flushall
   ```

## 🎉 **You're All Set!**

Your Redis Stack setup is perfect for:
- ✅ **Chat history storage**
- ✅ **Session management**
- ✅ **Visual monitoring**
- ✅ **Production readiness**

**Next steps:**
1. Set your environment variables
2. Test the connection
3. Run your FastAPI app
4. Monitor with RedisInsight! 🚀
