from pydantic import BaseModel
from typing import Optional, List


class SearchResponseItem(BaseModel):
    """Individual search result item."""
    id: str
    score: float
    title: Optional[str] = None
    image_url: Optional[str] = None
    page_link: Optional[str] = None
    source_domain: Optional[str] = None
    snippet: Optional[str] = None
    search_type: str


class SearchResponse(BaseModel):
    """Search API response."""
    results: List[SearchResponseItem]
    query: str
    total_results: int
    search_type: str  # "hybrid", "vector", "google"


class SearchRequest(BaseModel):
    """Search request parameters."""
    query: str
    top_k: int = 10
    num_results: int = 20
    search_type: str = "hybrid"  # "hybrid", "vector", "google"
