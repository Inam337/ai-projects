"""
LangChain tool wrapper for search functionality.
"""
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.services.search_service import search_service
from app.core.logging import logger


class SearchToolInput(BaseModel):
    """Input schema for the search tool."""
    query: str = Field(description="The search query to find interior design products, furniture, or decor items")
    search_type: str = Field(
        default="hybrid", 
        description="Type of search: 'hybrid' (combines vector and Google search), 'vector' (semantic search only), or 'google' (web search only)"
    )
    top_k: int = Field(
        default=5, 
        description="Number of results to return (1-20)"
    )


class SearchTool(BaseTool):
    """Tool for searching interior design products and furniture."""
    
    name: str = "interior_design_search"
    description: str = (
        "Search for interior design products, furniture, decor items, and design inspiration. "
        "Use this tool when users ask about specific products, furniture, colors, styles, "
        "or when they need visual examples or product recommendations. "
        "The tool can search both a curated database of design items and real-time web results."
    )
    args_schema: Type[BaseModel] = SearchToolInput
    
    def _run(
        self, 
        query: str, 
        search_type: str = "hybrid", 
        top_k: int = 5,
        **kwargs: Any
    ) -> str:
        """Execute the search tool synchronously."""
        # Log that our MCP tool is being used (minimal logging)
        logger.info("MCP_SEARCH_TOOL_CALLED", tool_name="interior_design_search")
        
        try:
            # Validate inputs
            if not query or not query.strip():
                return "Error: Search query cannot be empty."
            
            if search_type not in ["hybrid", "vector", "google"]:
                return f"Error: Invalid search_type '{search_type}'. Must be 'hybrid', 'vector', or 'google'."
            
            if not (1 <= top_k <= 20):
                return f"Error: top_k must be between 1 and 20, got {top_k}."
            
            # Perform search
            import asyncio
            result = asyncio.run(search_service.search(
                query=query.strip(),
                search_type=search_type,
                top_k=top_k,
                num_results=20
            ))
            
            if not result.results:
                return f"No results found for query: '{query}'"
            
            # Format results for the agent
            formatted_results = []
            for i, item in enumerate(result.results[:top_k], 1):
                result_text = f"{i}. {item.title or 'Untitled'}"
                if item.snippet:
                    result_text += f"\n   Description: {item.snippet}"
                if item.source_domain:
                    result_text += f"\n   Source: {item.source_domain}"
                if item.image_url:
                    result_text += f"\n   Image: {item.image_url}"
                if item.page_link:
                    result_text += f"\n   Link: {item.page_link}"
                result_text += f"\n   Relevance Score: {item.score:.2f}"
                formatted_results.append(result_text)
            
            response = f"Found {len(result.results)} results for '{query}':\n\n" + "\n\n".join(formatted_results)
            
            logger.info(
                "search_tool_executed",
                query=query,
                search_type=search_type,
                results_count=len(result.results)
            )
            
            return response
            
        except Exception as e:
            logger.error("search_tool_failed", query=query, error=str(e), exc_info=True)
            return f"Search failed: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        search_type: str = "hybrid", 
        top_k: int = 5,
        **kwargs: Any
    ) -> str:
        """Execute the search tool asynchronously."""
        # Log that our MCP tool is being used (minimal logging)
        logger.info("MCP_SEARCH_TOOL_CALLED_ASYNC", tool_name="interior_design_search")
        
        try:
            # Validate inputs
            if not query or not query.strip():
                return "Error: Search query cannot be empty."
            
            if search_type not in ["hybrid", "vector", "google"]:
                return f"Error: Invalid search_type '{search_type}'. Must be 'hybrid', 'vector', or 'google'."
            
            if not (1 <= top_k <= 20):
                return f"Error: top_k must be between 1 and 20, got {top_k}."
            
            # Perform search
            result = await search_service.search(
                query=query.strip(),
                search_type=search_type,
                top_k=top_k,
                num_results=20
            )
            
            if not result.results:
                return f"No results found for query: '{query}'"
            
            # Format results for the agent
            formatted_results = []
            for i, item in enumerate(result.results[:top_k], 1):
                result_text = f"{i}. {item.title or 'Untitled'}"
                if item.snippet:
                    result_text += f"\n   Description: {item.snippet}"
                if item.source_domain:
                    result_text += f"\n   Source: {item.source_domain}"
                if item.image_url:
                    result_text += f"\n   Image: {item.image_url}"
                if item.page_link:
                    result_text += f"\n   Link: {item.page_link}"
                result_text += f"\n   Relevance Score: {item.score:.2f}"
                formatted_results.append(result_text)
            
            response = f"Found {len(result.results)} results for '{query}':\n\n" + "\n\n".join(formatted_results)
            
            logger.info(
                "search_tool_executed",
                query=query,
                search_type=search_type,
                results_count=len(result.results)
            )
            
            return response
            
        except Exception as e:
            logger.error("search_tool_failed", query=query, error=str(e), exc_info=True)
            return f"Search failed: {str(e)}"


# Create the tool instance
interior_design_search_tool = SearchTool()
