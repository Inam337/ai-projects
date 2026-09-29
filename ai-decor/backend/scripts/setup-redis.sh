#!/bin/bash

# Redis setup script for Interior Design AI Assistant

echo "🔧 Setting up Redis for chat history storage..."

# Check if Redis is already running
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is already running"
    redis-cli ping
else
    echo "📦 Installing Redis..."
    
    # Detect OS and install Redis
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew > /dev/null; then
            brew install redis
            brew services start redis
        else
            echo "❌ Homebrew not found. Please install Redis manually:"
            echo "   brew install redis"
            echo "   brew services start redis"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get > /dev/null; then
            sudo apt-get update
            sudo apt-get install -y redis-server
            sudo systemctl start redis-server
            sudo systemctl enable redis-server
        elif command -v yum > /dev/null; then
            sudo yum install -y redis
            sudo systemctl start redis
            sudo systemctl enable redis
        else
            echo "❌ Package manager not found. Please install Redis manually"
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install Redis manually"
        exit 1
    fi
fi

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is working correctly!"
    echo "📊 Redis info:"
    redis-cli info server | grep redis_version
    echo ""
    echo "🚀 Redis is ready for chat history storage!"
    echo "💡 Default configuration:"
    echo "   - Host: localhost"
    echo "   - Port: 6379"
    echo "   - Database: 0"
    echo "   - TTL: 24 hours (86400 seconds)"
else
    echo "❌ Redis connection failed"
    exit 1
fi
