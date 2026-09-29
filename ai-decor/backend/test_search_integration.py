"""
Test script to verify search tool integration.
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.search_service import search_service
from app.core.langgraph.tools.search_tool import interior_design_search_tool


async def test_search_service():
    """Test the search service directly."""
    print("🔍 Testing Search Service...")
    
    try:
        # Test hybrid search
        result = await search_service.search(
            query="modern sofa",
            search_type="hybrid",
            top_k=3,
            num_results=5
        )
        
        print(f"✅ Search service working!")
        print(f"   Query: {result.query}")
        print(f"   Results: {result.total_results}")
        print(f"   Search type: {result.search_type}")
        
        if result.results:
            print(f"   First result: {result.results[0].title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search service failed: {e}")
        return False


def test_langchain_tool():
    """Test the LangChain tool wrapper."""
    print("\n🤖 Testing LangChain Tool...")
    
    try:
        # Test the tool
        result = interior_design_search_tool._run(
            query="rustic coffee table",
            search_type="hybrid",
            top_k=2
        )
        
        print(f"✅ LangChain tool working!")
        print(f"   Result preview: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain tool failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Testing Search Tool Integration\n")
    
    # Test search service
    service_ok = await test_search_service()
    
    # Test LangChain tool
    tool_ok = test_langchain_tool()
    
    print(f"\n📊 Test Results:")
    print(f"   Search Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    print(f"   LangChain Tool: {'✅ PASS' if tool_ok else '❌ FAIL'}")
    
    if service_ok and tool_ok:
        print(f"\n🎉 All tests passed! Search tool is ready to use.")
    else:
        print(f"\n⚠️  Some tests failed. Check the configuration.")


if __name__ == "__main__":
    asyncio.run(main())
