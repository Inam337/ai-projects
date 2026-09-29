import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn

from models import Person, PersonProfile, SearchResults, CompanyMatchQuery, CompanyMatchResult
from data_loader import DataLoader
from scoring_engine import ScoringEngine
from people_finder import PeopleFinderEngine
from company_matcher import CompanyMatchmakingEngine
from query_manager import QueryManager
from enhanced_search import EnhancedSearchEngine
from hybrid_search import HybridRetrievalEngine
from llm_query_parser import LLMQueryParser, ParsedQuery
from query_executor import QueryExecutor

# Optional vector search - lazy import to avoid startup errors
VECTOR_SEARCH_AVAILABLE = False
VectorSearchEngine = None

def _try_import_vector_search():
    """Try to import vector search module using importlib"""
    global VECTOR_SEARCH_AVAILABLE, VectorSearchEngine
    try:
        import importlib
        vector_search_module = importlib.import_module('vector_search')
        VectorSearchEngine = vector_search_module.VectorSearchEngine
        VECTOR_SEARCH_AVAILABLE = True
        return True
    except ImportError as e:
        print(f"Warning: Vector search not available: {e}")
        print("Vector search features will be disabled. Install PyTorch and compatible dependencies to enable.")
        VECTOR_SEARCH_AVAILABLE = False
        VectorSearchEngine = None
        return False
    except Exception as e:
        print(f"Warning: Could not load vector search module: {e}")
        VECTOR_SEARCH_AVAILABLE = False
        VectorSearchEngine = None
        return False

app = FastAPI(
    title="People Finder & Company Matchmaking API",
    description="API for finding professionals and matching companies with people",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global components
data_loader = DataLoader()
scoring_engine = ScoringEngine()
people_finder = None
company_matcher = None
enhanced_search = None
vector_search = None
hybrid_search = None
query_manager = QueryManager()
llm_parser = None
query_executor = None

# Configuration file for scoring weights
CONFIG_FILE = "config.json"


def person_to_profile(person: Person, relevance_score: Optional[float] = None, explanation: Optional[str] = None) -> PersonProfile:
    """Helper function to convert Person to PersonProfile with all fields"""
    return PersonProfile(
        id=person.id,
        firstName=person.firstName,
        lastName=person.lastName,
        full_name=f"{person.firstName} {person.lastName}",
        job_title=person.job_title,
        headline=person.headline,
        location=person.location,
        industry=person.industry,
        current_company=person.current_company,
        seniority=person.seniority,
        gender=person.gender,
        profilePictureUrl=person.profilePictureUrl,
        linkedinUrl=person.linkedinUrl,
        account_name_profile=person.account_name_profile,
        account_name_clean=person.account_name_clean,
        website=person.website,
        linkedin_url=person.linkedin_url,
        facebook_url=person.facebook_url,
        twitter_url=person.twitter_url,
        account_city=person.account_city,
        account_state=person.account_state,
        account_country=person.account_country,
        postal_code=person.postal_code,
        account_address=person.account_address,
        keywords=person.keywords,
        account_phone=person.account_phone,
        technologies=person.technologies,
        annual_revenue=person.annual_revenue,
        sic_code=person.sic_code,
        naics_code=person.naics_code,
        account_description=person.account_description,
        founded_year=person.founded_year,
        logo_url=person.logo_url,
        subsidiary_of=person.subsidiary_of,
        employee_count=person.employee_count,
        importDate=person.importDate,
        premium=person.premium,
        jobSeeker=person.jobSeeker,
        salesNavigatorId=person.salesNavigatorId,
        profile_completeness=person.profile_completeness,
        relevance_score=relevance_score,
        explanation=explanation
    )


def load_config():
    """Load configuration from file or use defaults"""
    default_config = {
        "scoring_weights": {
            "industry_alignment": 0.35,
            "role_relevance": 0.30,
            "location_proximity": 0.15,
            "profile_completeness": 0.10,
            "recency_freshness": 0.05,
            "special_flags": 0.05
        }
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        except:
            return default_config
    return default_config


def save_config(config: dict):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def initialize_engines():
    """Initialize search engines after data is loaded"""
    global people_finder, company_matcher, enhanced_search, vector_search, hybrid_search, llm_parser, query_executor
    
    if data_loader.people and scoring_engine:
        # Initialize basic engines (backward compatibility)
        people_finder = PeopleFinderEngine(data_loader.people, scoring_engine)
        enhanced_search = EnhancedSearchEngine(data_loader.people, scoring_engine)
        
        # Try to initialize vector search if available
        if _try_import_vector_search() and VectorSearchEngine:
            try:
                vector_search = VectorSearchEngine(data_loader.people, scoring_engine)
                print("Vector search engine initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize vector search: {e}")
                vector_search = None
        else:
            vector_search = None
        
        # Initialize hybrid retrieval engine (primary search method)
        # Uses BM25 lexical + optional semantic re-ranking
        hybrid_search = HybridRetrievalEngine(
            data_loader.people,
            scoring_engine,
            vector_search
        )
        print("Hybrid retrieval engine initialized (BM25 + optional semantic)")
    
    if data_loader.people and data_loader.pakistani_companies and scoring_engine:
        company_matcher = CompanyMatchmakingEngine(
            data_loader.people,
            data_loader.pakistani_companies,
            scoring_engine
        )
    
    # Initialize LLM parser and query executor
    global llm_parser, query_executor
    try:
        import os
        llm_backend = os.getenv("LLM_BACKEND", "rule_based")  # "ollama", "lmstudio", "rule_based"
        llm_url = os.getenv("LLM_URL", "http://localhost:11434")
        
        llm_parser = LLMQueryParser(llm_backend=llm_backend, llm_url=llm_url, data_dir=data_loader.data_dir)
        if llm_parser.llm_available:
            print(f"✓ LLM parser: Enabled ({llm_backend})")
        else:
            print(f"✓ LLM parser: Using rule-based fallback ({llm_backend} not available)")
        
        if hybrid_search and company_matcher:
            query_executor = QueryExecutor(hybrid_search, company_matcher, data_loader, llm_parser)
            print("✓ Query executor: Initialized")
    except Exception as e:
        print(f"Warning: Could not initialize LLM parser: {e}")
        llm_parser = None
        query_executor = None


# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Load datasets and initialize engines on startup"""
    print("Loading datasets...")
    data_loader.load_all()
    
    # Load configuration
    config = load_config()
    if "scoring_weights" in config:
        scoring_engine.update_weights(config["scoring_weights"])
    
    # Initialize engines
    initialize_engines()
    
    # Print status
    print(f"✓ Loaded {len(data_loader.people)} people profiles")
    print(f"✓ Loaded {len(data_loader.pakistani_companies)} Pakistani companies")
    if hybrid_search:
        if vector_search:
            print("✓ Hybrid search: Enabled (BM25 + semantic)")
        else:
            print("✓ Hybrid search: Enabled (BM25 only, semantic disabled)")
    if vector_search:
        print("✓ Vector search: Enabled")
    else:
        print("✓ Vector search: Disabled (optional feature)")
    print("✓ Enhanced search: Enabled")
    print("✓ Fuzzy search: Enabled")
    print("✓ Deduplication: Applied")
    print("API ready!")


# Request/Response Models
class SearchQuery(BaseModel):
    query: str
    max_results: Optional[int] = 10
    min_completeness: Optional[float] = 50.0


class SaveQueryRequest(BaseModel):
    query: str
    name: Optional[str] = None
    query_type: Optional[str] = "people_search"


class RenameQueryRequest(BaseModel):
    new_name: str


class ScoringWeights(BaseModel):
    industry_alignment: float
    role_relevance: float
    location_proximity: float
    profile_completeness: float


class CompanyInfo(BaseModel):
    id: str
    account_name_profile: str
    account_name_clean: Optional[str] = None
    industry: Optional[str] = None
    account_description: Optional[str] = None
    account_services: Optional[str] = None
    account_city: Optional[str] = None
    account_country: Optional[str] = None
    employee_count: Optional[int] = None
    logo_url: Optional[str] = None


class AutocompleteRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10


class LLMSearchQuery(BaseModel):
    query: str
    max_results: Optional[int] = 10
    use_llm: Optional[bool] = True  # Whether to use LLM parsing (falls back to rule-based if LLM unavailable)


class FilteredSearchRequest(BaseModel):
    query: str
    filter_type: str  # "name", "job_title", "company"
    max_results: Optional[int] = 10
    min_completeness: Optional[float] = 50.0


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "People Finder & Company Matchmaking API",
        "status": "running",
        "version": "1.0.0",
        "data_loaded": {
            "people": len(data_loader.people),
            "companies": len(data_loader.companies),
            "pakistani_companies": len(data_loader.pakistani_companies)
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Query Statistics Endpoints
@app.get("/api/query/stats")
async def get_query_statistics():
    """Get overall query statistics"""
    if not llm_parser:
        raise HTTPException(status_code=503, detail="LLM parser not available")
    
    stats = llm_parser.get_query_statistics()
    if stats is None:
        return {"message": "Query statistics not available"}
    
    return stats


@app.get("/api/query/popular")
async def get_popular_queries(limit: int = 10):
    """Get most popular queries"""
    if not llm_parser:
        raise HTTPException(status_code=503, detail="LLM parser not available")
    
    return {"queries": llm_parser.get_popular_queries(limit)}


@app.get("/api/query/recent")
async def get_recent_queries(limit: int = 10):
    """Get most recent queries"""
    if not llm_parser:
        raise HTTPException(status_code=503, detail="LLM parser not available")
    
    return {"queries": llm_parser.get_recent_queries(limit)}


# LLM-Powered Search Endpoint (Objective 1 & 2)
@app.post("/api/search/llm", response_model=SearchResults)
async def search_with_llm(query: LLMSearchQuery):
    """
    Advanced search using LLM query parsing
    Supports Objective 1 (finding Saudi professionals) and Objective 2 (company matching)
    """
    if not hybrid_search or not query_executor:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        # Parse query with LLM or rule-based parser
        if query.use_llm and llm_parser:
            parsed_query = llm_parser.parse(query.query)
        elif llm_parser:
            parsed_query = llm_parser.parse(query.query)  # Will use rule-based fallback
        else:
            raise HTTPException(status_code=503, detail="LLM parser not available")
        
        # Execute parsed query (statistics will be recorded automatically)
        results = query_executor.execute(parsed_query, max_results=query.max_results, 
                                        original_query=query.query)
        
        # Convert SearchResult to PersonProfile
        person_profiles = []
        for result in results:
            person_profiles.append(person_to_profile(
                result.person,
                relevance_score=result.relevance_score,
                explanation=result.explanation
            ))
        
        return SearchResults(
            query=query.query,
            results=person_profiles,
            total_results=len(person_profiles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


# People Finder Endpoint
@app.post("/api/search/people", response_model=SearchResults)
async def search_people(query: SearchQuery):
    """
    Search for professionals based on natural language query
    Uses LLM query parser to extract filters (including gender) and applies them
    Uses hybrid retrieval pipeline: BM25 lexical → semantic re-rank → scoring
    """
    if not hybrid_search:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        # Use query executor if available (supports gender filtering and other filters)
        if query_executor and llm_parser:
            # Parse query to extract gender and other filters
            parsed_query = llm_parser.parse(query.query)
            
            # Debug: Log extracted gender
            if parsed_query.gender:
                print(f"✓ Gender filter extracted: '{parsed_query.gender}' from query: '{query.query}'")
            
            # Execute query with filters applied
            results = query_executor.execute(
                parsed_query, 
                max_results=query.max_results,
                original_query=query.query
            )
        else:
            # Fallback to direct hybrid search (no gender filtering)
            print("Warning: Using direct hybrid search without query parsing (gender filtering disabled)")
            results = hybrid_search.hybrid_search(
                query.query,
                max_results=query.max_results,
                min_completeness=query.min_completeness
            )
        
        # Convert SearchResult to PersonProfile
        person_profiles = []
        for result in results:
            person_profiles.append(person_to_profile(
                result.person,
                relevance_score=result.relevance_score,
                explanation=result.explanation
            ))
        
        return SearchResults(
            query=query.query,
            results=person_profiles,
            total_results=len(person_profiles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


# Company Matchmaking Endpoint
@app.post("/api/match/company", response_model=CompanyMatchResult)
async def match_company_with_people(query: CompanyMatchQuery):
    """
    Find relevant professionals for a Pakistani IT company
    """
    if not company_matcher:
        raise HTTPException(status_code=503, detail="Matchmaking engine not initialized")
    
    try:
        results = company_matcher.find_matches(
            query.company_name,
            query.target_city,
            query.max_results
        )
        
        # Get company info for matching criteria
        company = data_loader.get_pakistani_company_by_name(query.company_name)
        matching_criteria = ""
        if company:
            matching_criteria = company_matcher.generate_matching_criteria(company, query.target_city)
        
        # Convert SearchResult to PersonProfile
        person_profiles = []
        for result in results:
            person_profiles.append(person_to_profile(
                result.person,
                relevance_score=result.relevance_score,
                explanation=result.explanation
            ))
        
        return CompanyMatchResult(
            company_name=query.company_name,
            matched_professionals=person_profiles,
            matching_criteria=matching_criteria
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matchmaking error: {str(e)}")


# Get person by ID
@app.get("/api/people/{person_id}", response_model=PersonProfile)
async def get_person(person_id: str):
    """
    Get a specific person's profile by ID
    """
    person = data_loader.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return person_to_profile(person)


# Get company by name
@app.get("/api/companies/{company_name}", response_model=CompanyInfo)
async def get_company(company_name: str):
    """
    Get company information by name
    """
    company = data_loader.get_pakistani_company_by_name(company_name)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return CompanyInfo(
        id=company.id,
        account_name_profile=company.account_name_profile,
        account_name_clean=company.account_name_clean,
        industry=company.industry,
        account_description=company.account_description,
        account_services=company.account_services,
        account_city=company.account_city,
        account_country=company.account_country,
        employee_count=company.employee_count,
        logo_url=company.logo_url
    )


# List Pakistani companies
@app.get("/api/companies")
async def list_companies():
    """List all Pakistani companies"""
    companies = []
    for company in data_loader.pakistani_companies:
        companies.append({
            "id": company.id,
            "account_name_profile": company.account_name_profile,
            "account_name_clean": company.account_name_clean,
            "industry": company.industry,
            "account_city": company.account_city
        })
    return {"companies": companies, "total": len(companies)}


# Query Management Endpoints
@app.post("/api/queries/save")
async def save_query(request: SaveQueryRequest):
    """Save a search query"""
    query_id = query_manager.save_query(
        request.query,
        request.name,
        request.query_type
    )
    return {"query_id": query_id, "message": "Query saved successfully"}


@app.get("/api/queries")
async def list_queries(query_type: Optional[str] = None):
    """List all saved queries"""
    queries = query_manager.list_queries(query_type)
    return {"queries": queries, "total": len(queries)}


@app.get("/api/queries/{query_id}")
async def get_query(query_id: str):
    """Get a saved query by ID"""
    query = query_manager.get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query


@app.put("/api/queries/{query_id}/rename")
async def rename_query(query_id: str, request: RenameQueryRequest):
    """Rename a saved query"""
    success = query_manager.rename_query(query_id, request.new_name)
    if not success:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"message": "Query renamed successfully"}


@app.delete("/api/queries/{query_id}")
async def delete_query(query_id: str):
    """Delete a saved query"""
    success = query_manager.delete_query(query_id)
    if not success:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"message": "Query deleted successfully"}


# Scoring Configuration Endpoints
@app.get("/api/scoring/weights")
async def get_scoring_weights():
    """Get current scoring weights"""
    return {"weights": scoring_engine.weights}


@app.put("/api/scoring/weights")
async def update_scoring_weights(weights: ScoringWeights):
    """Update scoring weights"""
    new_weights = {
        "industry_alignment": weights.industry_alignment,
        "role_relevance": weights.role_relevance,
        "location_proximity": weights.location_proximity,
        "profile_completeness": weights.profile_completeness
    }
    
    scoring_engine.update_weights(new_weights)
    
    # Save to config file
    config = load_config()
    config["scoring_weights"] = new_weights
    save_config(config)
    
    # Reinitialize engines with new weights
    initialize_engines()
    
    return {"message": "Scoring weights updated successfully", "weights": new_weights}


# Autocomplete Endpoint
@app.post("/api/autocomplete")
async def get_autocomplete_suggestions(request: AutocompleteRequest):
    """Get autocomplete suggestions for names, job titles, and companies"""
    if not enhanced_search:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        suggestions = enhanced_search.get_autocomplete_suggestions(
            request.query,
            request.max_results
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete error: {str(e)}")


# Filtered Search Endpoints
@app.post("/api/search/filtered", response_model=SearchResults)
async def filtered_search(request: FilteredSearchRequest):
    """Search with filters: name, job_title, or company"""
    if not enhanced_search:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    try:
        if request.filter_type == "name":
            results = enhanced_search.search_by_name(
                request.query,
                request.max_results
            )
        elif request.filter_type == "job_title":
            results = enhanced_search.search_by_job_title(
                request.query,
                request.max_results
            )
        elif request.filter_type == "company":
            results = enhanced_search.search_by_company(
                request.query,
                request.max_results
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid filter_type. Must be 'name', 'job_title', or 'company'")
        
        # Convert SearchResult to PersonProfile
        person_profiles = []
        for result in results:
            person_profiles.append(person_to_profile(
                result.person,
                relevance_score=result.relevance_score,
                explanation=result.explanation
            ))
        
        return SearchResults(
            query=request.query,
            results=person_profiles,
            total_results=len(person_profiles)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtered search error: {str(e)}")


# Enhanced Search Endpoint (using vector search)
@app.post("/api/search/enhanced", response_model=SearchResults)
async def enhanced_search_endpoint(query: SearchQuery):
    """Enhanced search using vector similarity and semantic matching"""
    if not vector_search:
        raise HTTPException(
            status_code=503, 
            detail="Vector search engine not available. Install PyTorch and sentence-transformers to enable this feature."
        )
    
    try:
        results = vector_search.hybrid_search(
            query.query,
            query.max_results or 10,
            query.min_completeness or 50.0
        )
        
        # Convert SearchResult to PersonProfile
        person_profiles = []
        for result in results:
            person_profiles.append(person_to_profile(
                result.person,
                relevance_score=result.relevance_score,
                explanation=result.explanation
            ))
        
        return SearchResults(
            query=query.query,
            results=person_profiles,
            total_results=len(person_profiles)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced search error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
