"""
Test Google search functionality directly.
"""
import os
import sys

# Add the search_tool directory to the Python path
search_tool_path = os.path.join(os.path.dirname(__file__), 'search_tool')
if search_tool_path not in sys.path:
    sys.path.append(search_tool_path)

def test_google_search():
    """Test Google search directly."""
    print("🔍 Testing Google Search...")
    
    try:
        from search import search_engine_search
        
        # Test the search function
        results = search_engine_search("modern sofa", 5)
        
        print(f"✅ Google search working!")
        print(f"   Results count: {len(results)}")
        
        if results:
            print(f"   First result: {results[0].get('title', 'No title')}")
            print(f"   Image URL: {results[0].get('image_url', 'No image')}")
        else:
            print("   No results returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Google search failed: {e}")
        return False

def test_config():
    """Test if config is loading properly."""
    print("\n🔧 Testing Config...")
    
    try:
        import config
        
        print(f"   GOOGLE_API_KEY: {'✅ SET' if config.GOOGLE_API_KEY else '❌ NOT SET'}")
        print(f"   GOOGLE_CX: {'✅ SET' if config.GOOGLE_CX else '❌ NOT SET'}")
        
        if config.GOOGLE_API_KEY and config.GOOGLE_CX:
            print("   ✅ Config is properly loaded")
            return True
        else:
            print("   ❌ Missing Google API credentials")
            return False
            
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Testing Google Search Integration\n")
    
    # Test config first
    config_ok = test_config()
    
    if config_ok:
        # Test Google search
        search_ok = test_google_search()
        
        if search_ok:
            print(f"\n🎉 Google search is working! Your MCP tool should now return real results.")
        else:
            print(f"\n⚠️  Google search failed. Check your API credentials.")
    else:
        print(f"\n💡 Set your environment variables:")
        print(f"   export GOOGLE_API_KEY='your-google-api-key'")
        print(f"   export GOOGLE_CX='your-google-cx-id'")

if __name__ == "__main__":
    main()
