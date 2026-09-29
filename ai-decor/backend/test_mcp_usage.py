"""
Test script to verify MCP search tool usage.
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.langgraph.tools.search_tool import interior_design_search_tool
from app.services.search_service import search_service


async def test_mcp_tool_directly():
    """Test the MCP tool directly."""
    print("🔍 Testing MCP Search Tool Directly...")
    
    try:
        # Test the tool directly
        result = interior_design_search_tool._run(
            query="modern sofa",
            search_type="google",
            top_k=3
        )
        
        print(f"✅ MCP Tool Result:")
        print(f"   Length: {len(result)} characters")
        print(f"   Preview: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Tool failed: {e}")
        return False


async def test_search_service():
    """Test the search service directly."""
    print("\n🌐 Testing Search Service...")
    
    try:
        result = await search_service.google_search("rustic coffee table", 5)
        
        print(f"✅ Search Service Result:")
        print(f"   Query: {result.query}")
        print(f"   Results: {result.total_results}")
        print(f"   Search Type: {result.search_type}")
        
        if result.results:
            print(f"   First Result: {result.results[0].title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search Service failed: {e}")
        return False


async def test_langchain_tool_integration():
    """Test if the tool is properly integrated with LangChain."""
    print("\n🤖 Testing LangChain Tool Integration...")
    
    try:
        # Check if tool is available
        print(f"   Tool Name: {interior_design_search_tool.name}")
        print(f"   Tool Description: {interior_design_search_tool.description[:100]}...")
        print(f"   Tool Args Schema: {interior_design_search_tool.args_schema}")
        
        # Test tool metadata
        print(f"   Tool Available: {hasattr(interior_design_search_tool, '_run')}")
        print(f"   Async Available: {hasattr(interior_design_search_tool, '_arun')}")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain Integration failed: {e}")
        return False


async def main():
    """Run all MCP verification tests."""
    print("🚀 Verifying MCP Search Tool Usage\n")
    
    # Test 1: Direct tool usage
    tool_ok = await test_mcp_tool_directly()
    
    # Test 2: Search service
    service_ok = await test_search_service()
    
    # Test 3: LangChain integration
    integration_ok = await test_langchain_tool_integration()
    
    print(f"\n📊 MCP Verification Results:")
    print(f"   Direct Tool Usage: {'✅ PASS' if tool_ok else '❌ FAIL'}")
    print(f"   Search Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    print(f"   LangChain Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if tool_ok and service_ok and integration_ok:
        print(f"\n🎉 MCP Search Tool is properly integrated and working!")
        print(f"   Look for '🔍 MCP SEARCH TOOL CALLED' messages in your logs")
        print(f"   when the AI agent uses search functionality.")
    else:
        print(f"\n⚠️  Some MCP components failed. Check the configuration.")


if __name__ == "__main__":
    asyncio.run(main())
