"""
Hybrid Retrieval Pipeline
Phase 3: Two-stage retrieval (BM25 lexical → semantic re-ranking)

This module implements the hybrid retrieval pipeline:
1. First stage: BM25 lexical search (fast candidate set ~200)
2. Second stage: Semantic re-ranking using FAISS (top 5-10)

Falls back to pure lexical if embeddings unavailable.
"""

from typing import List, Optional
from models import Person, SearchResult
from scoring_engine import ScoringEngine
from bm25_search import BM25SearchEngine

# Optional vector search import
try:
    from vector_search import VectorSearchEngine
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    VectorSearchEngine = None


class HybridRetrievalEngine:
    """
    Hybrid retrieval engine combining BM25 lexical search with semantic re-ranking
    """
    
    def __init__(self, people: List[Person], scoring_engine: ScoringEngine, 
                 vector_search: Optional[VectorSearchEngine] = None):
        """
        Initialize hybrid retrieval engine
        
        Args:
            people: List of Person objects
            scoring_engine: ScoringEngine instance for final scoring
            vector_search: Optional VectorSearchEngine for semantic re-ranking
        """
        self.people = people
        self.scoring_engine = scoring_engine
        
        # Initialize BM25 lexical search (always available)
        self.bm25_engine = BM25SearchEngine(people)
        
        # Optional semantic search
        self.vector_search = vector_search
        self.use_semantic = VECTOR_SEARCH_AVAILABLE and vector_search is not None
    
    def hybrid_search(self, query: str, max_results: int = 10, 
                     min_completeness: float = 50.0,
                     candidate_size: int = 200,
                     gender_filter: Optional[str] = None) -> List[SearchResult]:
        """
        Perform hybrid search: BM25 lexical → semantic re-rank → final scoring
        
        Args:
            query: Search query string
            max_results: Final number of results to return
            min_completeness: Minimum profile completeness threshold
            candidate_size: Number of candidates from BM25 stage
            gender_filter: Optional gender filter ("male" or "female")
        
        Returns:
            List of SearchResult objects sorted by relevance score
        """
        # Stage 1: BM25 lexical retrieval (fast candidate set)
        candidates = self.bm25_engine.get_candidate_set(query, candidate_size)
        
        # Filter by completeness threshold
        filtered_candidates = [
            p for p in candidates 
            if p.profile_completeness >= min_completeness
        ]
        
        # Early gender filtering if specified (more efficient than filtering later)
        if gender_filter:
            gender_normalization = {
                'f': 'female', 'female': 'female', 'females': 'female',
                'm': 'male', 'male': 'male', 'males': 'male'
            }
            query_gender_normalized = gender_normalization.get(gender_filter.lower().strip(), gender_filter.lower().strip())
            print(f"✓ Hybrid search: Applying gender filter '{gender_filter}' (normalized: '{query_gender_normalized}') - Candidates before filter: {len(filtered_candidates)}")
            
            gender_filtered = []
            skipped_no_gender = 0
            skipped_wrong_gender = 0
            for person in filtered_candidates:
                if not person.gender:
                    skipped_no_gender += 1
                    continue  # Skip if no gender data
                
                person_gender = str(person.gender).lower().strip()
                person_gender_normalized = gender_normalization.get(person_gender, person_gender)
                
                if person_gender_normalized == query_gender_normalized:
                    gender_filtered.append(person)
                else:
                    skipped_wrong_gender += 1
            
            filtered_candidates = gender_filtered
            print(f"✓ Hybrid search: After gender filter - Matched: {len(gender_filtered)}, Skipped (no gender): {skipped_no_gender}, Skipped (wrong gender): {skipped_wrong_gender}")
        
        if not filtered_candidates:
            return []
        
        # Stage 2: Semantic re-ranking (if available)
        if self.use_semantic and self.vector_search:
            # Get semantic matches from candidate set
            semantic_results = self.vector_search.semantic_search(
                query, 
                max_results=min(max_results * 3, len(filtered_candidates)),
                min_completeness=min_completeness
            )
            
            # Create person ID set from semantic results
            semantic_ids = {r.person.id for r in semantic_results}
            
            # Prioritize semantic matches, then add remaining BM25 candidates
            ranked_candidates = []
            seen_ids = set()
            
            # Add semantic matches first
            for result in semantic_results:
                if result.person.id not in seen_ids:
                    ranked_candidates.append(result.person)
                    seen_ids.add(result.person.id)
            
            # Add remaining BM25 candidates not in semantic results
            for person in filtered_candidates:
                if person.id not in seen_ids and len(ranked_candidates) < candidate_size:
                    ranked_candidates.append(person)
                    seen_ids.add(person.id)
            
            candidates = ranked_candidates[:candidate_size]
        else:
            # Pure lexical: use BM25 candidates directly
            candidates = filtered_candidates
        
        # Stage 3: Final scoring with comprehensive scoring engine
        final_results = []
        seen_ids = set()
        
        # Extract query components for scoring
        query_terms = self.bm25_engine._tokenize(query)
        location = self._extract_location(query)
        
        for person in candidates:
            # Skip duplicates
            if person.id in seen_ids:
                continue
            
            # Calculate comprehensive score
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, query_terms, location
            )
            
            # Generate explanation
            explanation = self.scoring_engine.generate_explanation(
                person, breakdown, query_terms, location
            )
            
            final_results.append(SearchResult(
                person=person,
                relevance_score=round(score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
            
            seen_ids.add(person.id)
        
        # Sort by relevance score descending
        final_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Return top results
        return final_results[:max_results]
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query if mentioned"""
        # Common city/country names
        locations = [
            'riyadh', 'jeddah', 'dammam', 'khobar', 'mecca', 'medina', 
            'saudi', 'ksa', 'pakistan', 'karachi', 'lahore', 'islamabad',
            'dubai', 'abu dhabi', 'doha', 'kuwait', 'bahrain'
        ]
        
        query_lower = query.lower()
        for loc in locations:
            if loc in query_lower:
                return loc.capitalize()
        
        return None
    
    def search_lexical_only(self, query: str, max_results: int = 10,
                           min_completeness: float = 50.0) -> List[SearchResult]:
        """
        Perform pure lexical search (BM25 + scoring) without semantic re-ranking
        Useful when vector search is unavailable
        """
        # Get BM25 candidates
        candidates = self.bm25_engine.get_candidate_set(query, max_results * 5)
        
        # Filter by completeness
        filtered_candidates = [
            p for p in candidates 
            if p.profile_completeness >= min_completeness
        ]
        
        # Score and rank
        final_results = []
        seen_ids = set()
        
        query_terms = self.bm25_engine._tokenize(query)
        location = self._extract_location(query)
        
        for person in filtered_candidates:
            if person.id in seen_ids:
                continue
            
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, query_terms, location
            )
            
            explanation = self.scoring_engine.generate_explanation(
                person, breakdown, query_terms, location
            )
            
            final_results.append(SearchResult(
                person=person,
                relevance_score=round(score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
            
            seen_ids.add(person.id)
        
        final_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return final_results[:max_results]



