"""
Debug script to test search configuration and identify issues.
"""
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_environment_variables():
    """Test if environment variables are set."""
    print("🔍 Testing Environment Variables:")
    
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    google_cx = os.getenv("GOOGLE_CX", "")
    
    print(f"   GOOGLE_API_KEY: {'✅ SET' if google_api_key else '❌ NOT SET'}")
    print(f"   GOOGLE_CX: {'✅ SET' if google_cx else '❌ NOT SET'}")
    
    if google_api_key and google_cx:
        print(f"   API Key length: {len(google_api_key)} characters")
        print(f"   CX length: {len(google_cx)} characters")
        return True
    else:
        print("   ❌ Missing required environment variables")
        return False

def test_fastapi_config():
    """Test if FastAPI config is loading the values."""
    print("\n🔧 Testing FastAPI Config:")
    
    try:
        from app.core.config import settings
        
        print(f"   GOOGLE_API_KEY: {'✅ SET' if settings.GOOGLE_API_KEY else '❌ NOT SET'}")
        print(f"   GOOGLE_CX: {'✅ SET' if settings.GOOGLE_CX else '❌ NOT SET'}")
        print(f"   DOWNLOAD_DIR: {settings.DOWNLOAD_DIR}")
        print(f"   CHROMA_PERSIST_DIRECTORY: {settings.CHROMA_PERSIST_DIRECTORY}")
        
        return bool(settings.GOOGLE_API_KEY and settings.GOOGLE_CX)
        
    except Exception as e:
        print(f"   ❌ Error loading FastAPI config: {e}")
        return False

def test_search_tool_config():
    """Test if search_tool config is working."""
    print("\n🔧 Testing Search Tool Config:")
    
    try:
        # Add search_tool to path
        search_tool_path = os.path.join(os.path.dirname(__file__), 'search_tool')
        if search_tool_path not in sys.path:
            sys.path.append(search_tool_path)
        
        import config
        
        print(f"   GOOGLE_API_KEY: {'✅ SET' if config.GOOGLE_API_KEY else '❌ NOT SET'}")
        print(f"   GOOGLE_CX: {'✅ SET' if config.GOOGLE_CX else '❌ NOT SET'}")
        print(f"   DOWNLOAD_DIR: {config.DOWNLOAD_DIR}")
        print(f"   CHROMA_PERSIST_DIRECTORY: {config.CHROMA_PERSIST_DIRECTORY}")
        
        return bool(config.GOOGLE_API_KEY and config.GOOGLE_CX)
        
    except Exception as e:
        print(f"   ❌ Error loading search_tool config: {e}")
        return False

def test_search_service():
    """Test the search service directly."""
    print("\n🌐 Testing Search Service:")
    
    try:
        from app.services.search_service import search_service
        
        print(f"   Search service available: {'✅ YES' if search_service.available else '❌ NO'}")
        
        if search_service.available:
            print("   ✅ Search service is properly configured")
            return True
        else:
            print("   ❌ Search service is not available")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing search service: {e}")
        return False

def test_search_tool_directly():
    """Test the search tool directly."""
    print("\n🔧 Testing Search Tool Directly:")
    
    try:
        from app.core.langgraph.tools.search_tool import interior_design_search_tool
        
        # Test the tool directly
        result = interior_design_search_tool._run(
            query="test query",
            search_type="google",
            top_k=3
        )
        
        print(f"   Tool result length: {len(result)} characters")
        print(f"   Result preview: {result[:100]}...")
        
        if "No results found" in result or "Search failed" in result:
            print("   ❌ Tool is returning empty/error results")
            return False
        else:
            print("   ✅ Tool is working")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing search tool: {e}")
        return False

def main():
    """Run all debug tests."""
    print("🚀 Debugging Search Configuration\n")
    
    # Test 1: Environment variables
    env_ok = test_environment_variables()
    
    # Test 2: FastAPI config
    config_ok = test_fastapi_config()
    
    # Test 3: Search tool config
    search_config_ok = test_search_tool_config()
    
    # Test 4: Search service
    service_ok = test_search_service()
    
    # Test 5: Search tool directly
    tool_ok = test_search_tool_directly()
    
    print(f"\n📊 Debug Results:")
    print(f"   Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   FastAPI Config: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Search Tool Config: {'✅ PASS' if search_config_ok else '❌ FAIL'}")
    print(f"   Search Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    print(f"   Search Tool: {'✅ PASS' if tool_ok else '❌ FAIL'}")
    
    if not env_ok:
        print(f"\n💡 Solution: Set your environment variables:")
        print(f"   export GOOGLE_API_KEY='your-google-api-key'")
        print(f"   export GOOGLE_CX='your-google-cx-id'")
    elif not config_ok:
        print(f"\n💡 Solution: Check your .env file or environment setup")
    elif not service_ok:
        print(f"\n💡 Solution: Search service configuration issue")
    else:
        print(f"\n🎉 All tests passed! Your search should be working.")

if __name__ == "__main__":
    main()
