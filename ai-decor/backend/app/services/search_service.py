"""
Search service for integrating search functionality with the main FastAPI app.
"""
import os
import sys
from typing import List, Dict, Any
from app.core.logging import logger
from app.schemas.search import SearchResponseItem, SearchResponse

# Add the search_tool directory to the Python path
search_tool_path = os.path.join(os.path.dirname(__file__), '..', '..', 'search_tool')
if search_tool_path not in sys.path:
    sys.path.append(search_tool_path)

try:
    from search import vector_search, search_engine_search, hybrid_search
    logger.info("Search tool module loaded successfully")
except ImportError as e:
    logger.warning(f"Search tool module not available: {e}")
    # Fallback functions for when search_tool is not available
    def vector_search(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        logger.info("Vector search fallback - returning empty results")
        return []
    
    def search_engine_search(query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        logger.info("Google search fallback - returning empty results")
        return []
    
    def hybrid_search(query: str, top_k: int = 10, num_results: int = 20) -> List[Dict[str, Any]]:
        logger.info("Hybrid search fallback - returning empty results")
        return []

# Alternative: OpenAI-based search service (DISABLED FOR NOW)
# class OpenAIEmbeddingSearch:
#     """Alternative search using OpenAI embeddings instead of sentence-transformers."""
#     
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.client = None
#         try:
#             from openai import OpenAI
#             self.client = OpenAI(api_key=api_key)
#         except ImportError:
#             logger.warning("OpenAI client not available")
#     
#     async def search_similar(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
#         """Search for similar documents using OpenAI embeddings."""
#         if not self.client:
#             return []
#         
#         try:
#             # Get query embedding
#             query_response = self.client.embeddings.create(
#                 model="text-embedding-3-small",
#                 input=query
#             )
#             query_embedding = query_response.data[0].embedding
#             
#             # Calculate similarities (simplified)
#             similarities = []
#             for doc in documents:
#                 # This is a simplified version - in practice you'd store embeddings
#                 # and calculate cosine similarity
#                 similarity = 0.8  # Placeholder
#                 similarities.append({**doc, "score": similarity})
#             
#             # Sort by similarity and return top_k
#             similarities.sort(key=lambda x: x["score"], reverse=True)
#             return similarities[:top_k]
#             
#         except Exception as e:
#             logger.error(f"OpenAI embedding search failed: {e}")
#             return []


class SearchService:
    """Service for handling search operations."""
    
    def __init__(self):
        """Initialize the search service."""
        self.available = self._check_search_availability()
        if not self.available:
            logger.warning("Search functionality is not available. Check search_tool configuration.")
    
    def _check_search_availability(self) -> bool:
        """Check if search functionality is available."""
        try:
            # Test if we can call the search functions (even if they return empty results)
            test_results = search_engine_search("test", 1)
            logger.info("Search service availability check passed")
            return True
        except Exception as e:
            logger.warning(f"Search availability check failed: {e}")
            return False
    
    async def search(
        self, 
        query: str, 
        search_type: str = "hybrid", 
        top_k: int = 10, 
        num_results: int = 20
    ) -> SearchResponse:
        """
        Perform search based on the specified type.
        
        Args:
            query: Search query string
            search_type: Type of search ("hybrid", "vector", "google")
            top_k: Number of results for vector search
            num_results: Number of results for Google search
            
        Returns:
            SearchResponse: Formatted search results
        """
        if not self.available:
            return SearchResponse(
                results=[],
                query=query,
                total_results=0,
                search_type=search_type
            )
        
        try:
            if search_type == "vector":
                # Vector search disabled - fallback to Google search
                logger.info("Vector search disabled, using Google search instead")
                raw_results = search_engine_search(query, num_results)
            elif search_type == "google":
                raw_results = search_engine_search(query, num_results)
            else:  # hybrid
                # Hybrid search disabled - use Google search only
                logger.info("Hybrid search disabled, using Google search only")
                raw_results = search_engine_search(query, num_results)
            
            # Convert to SearchResponseItem objects
            results = [
                SearchResponseItem(**result) for result in raw_results
            ]
            
            logger.info(
                "search_completed",
                query=query,
                search_type=search_type,
                results_count=len(results)
            )
            
            return SearchResponse(
                results=results,
                query=query,
                total_results=len(results),
                search_type=search_type
            )
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return SearchResponse(
                results=[],
                query=query,
                total_results=0,
                search_type=search_type
            )
    
    async def vector_search(self, query: str, top_k: int = 10) -> SearchResponse:
        """Perform vector-only search (DISABLED - uses Google search instead)."""
        logger.info("Vector search is disabled, using Google search instead")
        return await self.search(query, "google", 0, 20)
    
    async def google_search(self, query: str, num_results: int = 20) -> SearchResponse:
        """Perform Google-only search."""
        return await self.search(query, "google", 0, num_results)
    
    async def hybrid_search(self, query: str, top_k: int = 10, num_results: int = 20) -> SearchResponse:
        """Perform hybrid search."""
        return await self.search(query, "hybrid", top_k, num_results)


# Global search service instance
search_service = SearchService()
