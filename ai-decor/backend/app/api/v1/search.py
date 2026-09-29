"""
Search API endpoints for the interior design application.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from app.schemas.search import SearchResponse, SearchResponseItem, SearchRequest
from app.services.search_service import search_service
from app.core.logging import logger
from app.core.limiter import limiter
from app.core.config import settings
from fastapi import Request

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["search"][0])
async def search(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    search_type: str = Query("hybrid", description="Search type: hybrid, vector, or google"),
    top_k: int = Query(10, ge=1, le=50, description="Number of vector search results"),
    num_results: int = Query(20, ge=1, le=100, description="Number of Google search results")
):
    """
    Perform hybrid search across vector database and Google search.
    
    This endpoint provides comprehensive search functionality for interior design
    products, combining vector similarity search with web search results.
    """
    try:
        logger.info(
            "search_request_received",
            query=q,
            search_type=search_type,
            top_k=top_k,
            num_results=num_results
        )
        
        result = await search_service.search(
            query=q,
            search_type=search_type,
            top_k=top_k,
            num_results=num_results
        )
        
        logger.info(
            "search_completed",
            query=q,
            results_count=result.total_results,
            search_type=search_type
        )
        
        return result
        
    except Exception as e:
        logger.error("search_request_failed", query=q, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/vector", response_model=SearchResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["search"][0])
async def vector_search(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Perform vector-only search using ChromaDB.
    
    This endpoint searches only the vector database for similar products
    based on semantic similarity.
    """
    try:
        logger.info("vector_search_request", query=q, top_k=top_k)
        
        result = await search_service.vector_search(q, top_k)
        
        logger.info("vector_search_completed", query=q, results_count=result.total_results)
        
        return result
        
    except Exception as e:
        logger.error("vector_search_failed", query=q, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


@router.get("/search/google", response_model=SearchResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["search"][0])
async def google_search(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    num_results: int = Query(20, ge=1, le=100, description="Number of results")
):
    """
    Perform Google-only search using Custom Search API.
    
    This endpoint searches only using Google Custom Search API for
    real-time web results.
    """
    try:
        logger.info("google_search_request", query=q, num_results=num_results)
        
        result = await search_service.google_search(q, num_results)
        
        logger.info("google_search_completed", query=q, results_count=result.total_results)
        
        return result
        
    except Exception as e:
        logger.error("google_search_failed", query=q, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Google search failed: {str(e)}")


@router.get("/search/health")
async def search_health():
    """
    Health check for search functionality.
    """
    try:
        is_available = search_service.available
        return {
            "status": "healthy" if is_available else "degraded",
            "search_available": is_available,
            "message": "Search service is operational" if is_available else "Search service is not available"
        }
    except Exception as e:
        logger.error("search_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "search_available": False,
            "message": f"Search health check failed: {str(e)}"
        }
