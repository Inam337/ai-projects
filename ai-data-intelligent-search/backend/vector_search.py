import numpy as np
import faiss
from typing import List, Optional
import pickle
import os
from models import Person, SearchResult
from scoring_engine import ScoringEngine

# Lazy import of sentence_transformers to avoid startup errors
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class VectorSearchEngine:
    """Vector database implementation using FAISS for semantic search"""
    
    def __init__(self, people: List[Person], scoring_engine: ScoringEngine):
        if not SENTENCE_TRANSFORMERS_AVAILABLE or SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is not available. "
                "Install it with: pip install sentence-transformers torch"
            )
        
        self.people = people
        self.scoring_engine = scoring_engine
        
        # Load or create sentence transformer model
        model_name = "all-MiniLM-L6-v2"  # Lightweight model for local use
        self.model = SentenceTransformer(model_name)
        
        # Initialize FAISS index
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Map index to person
        self.idx_to_person = {}
        
        # File paths
        self.index_file = "faiss_index.bin"
        self.embeddings_file = "embeddings.pkl"
        self.idx_map_file = "idx_map.pkl"
        
        self._build_or_load_index()
    
    def _get_text_for_embedding(self, person: Person) -> str:
        """Create searchable text representation for embedding"""
        parts = [
            person.firstName or "",
            person.lastName or "",
            person.job_title or "",
            person.headline or "",
            person.industry or "",
            person.current_company or "",
            person.location or "",
            person.seniority or ""
        ]
        return " ".join(filter(None, parts))
    
    def _build_or_load_index(self):
        """Build FAISS index or load from disk if exists"""
        if os.path.exists(self.index_file) and os.path.exists(self.embeddings_file):
            try:
                print("Loading existing FAISS index...")
                self.index = faiss.read_index(self.index_file)
                
                with open(self.idx_map_file, 'rb') as f:
                    self.idx_to_person = pickle.load(f)
                
                print(f"Loaded index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                print(f"Error loading index: {e}. Rebuilding...")
        
        print("Building new FAISS index...")
        self._build_index()
    
    def _build_index(self):
        """Build FAISS index from person data"""
        texts = []
        person_list = []
        
        for person in self.people:
            text = self._get_text_for_embedding(person)
            if text.strip():
                texts.append(text)
                person_list.append(person)
        
        if not texts:
            print("No text data to index")
            return
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} people...")
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        
        # Convert to numpy array
        embeddings = np.array(embeddings).astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Map index to person
        for idx, person in enumerate(person_list):
            self.idx_to_person[idx] = person
        
        # Save index
        faiss.write_index(self.index, self.index_file)
        
        with open(self.idx_map_file, 'wb') as f:
            pickle.dump(self.idx_to_person, f)
        
        print(f"Index built successfully with {self.index.ntotal} vectors")
    
    def semantic_search(self, query: str, max_results: int = 10, 
                       min_completeness: float = 50.0, gender_filter: Optional[str] = None) -> List[SearchResult]:
        """Perform semantic search using vector similarity with optional gender filtering"""
        if self.index.ntotal == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search in FAISS index - get more results when gender filter is active
        k = min(max_results * 20 if gender_filter else max_results * 2, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)
        
        # Gender normalization mapping
        gender_normalization = {
            'f': 'female', 'female': 'female', 'females': 'female', 'woman': 'female', 'women': 'female',
            'm': 'male', 'male': 'male', 'males': 'male', 'man': 'male', 'men': 'male',
        }
        
        query_gender_normalized = None
        if gender_filter:
            query_gender_normalized = gender_normalization.get(gender_filter.lower().strip(), gender_filter.lower().strip())
            print(f"✓ Vector search: Applying gender filter '{gender_filter}' (normalized: '{query_gender_normalized}')")
        
        # Convert distances to similarity scores (L2 distance to cosine similarity)
        # L2 distance on normalized vectors correlates with cosine distance
        # Smaller distance = higher similarity
        results = []
        seen_ids = set()
        gender_filtered_count = 0
        no_gender_count = 0
        
        for idx, distance in zip(indices[0], distances[0]):
            if idx == -1:  # Invalid index
                continue
            
            person = self.idx_to_person.get(idx)
            if not person:
                continue
            
            # Skip duplicates and incomplete profiles
            if person.id in seen_ids:
                continue
            
            if person.profile_completeness < min_completeness:
                continue
            
            # Apply gender filter if specified
            if query_gender_normalized:
                if not person.gender:
                    no_gender_count += 1
                    continue  # Exclude if no gender data
                
                person_gender = str(person.gender).lower().strip()
                person_gender_normalized = gender_normalization.get(person_gender, person_gender)
                
                # Only include if genders match exactly after normalization
                if person_gender_normalized != query_gender_normalized:
                    gender_filtered_count += 1
                    continue  # Exclude non-matching genders
            
            # Convert distance to similarity score (0-100)
            # Distance range typically 0-2 for normalized vectors
            similarity_score = max(0, 100 - (distance * 50))
            
            # Calculate traditional score (pass gender for scoring boost)
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, [query.lower()], None, query_gender=query_gender_normalized
            )
            
            # Combine semantic and traditional scores
            final_score = (similarity_score * 0.6) + (score * 0.4)
            
            explanation = f"Semantic match (similarity: {similarity_score:.1f}%)"
            
            results.append(SearchResult(
                person=person,
                relevance_score=round(final_score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
            
            seen_ids.add(person.id)
            
            if len(results) >= max_results:
                break
        
        # Debug: Log gender filtering stats
        if query_gender_normalized:
            print(f"✓ Vector search: After gender filter - Results: {len(results)}, Filtered: {gender_filtered_count}, No gender data: {no_gender_count}")
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def hybrid_search(self, query: str, max_results: int = 10,
                     min_completeness: float = 50.0, gender_filter: Optional[str] = None) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword matching with optional gender filtering"""
        # Get semantic results
        semantic_results = self.semantic_search(query, max_results * 2, min_completeness, gender_filter)
        
        # Boost exact/partial keyword matches
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        for result in semantic_results:
            person = result.person
            text = self._get_text_for_embedding(person).lower()
            
            # Check for exact matches
            if query_lower in text:
                result.relevance_score = min(100, result.relevance_score * 1.2)
            
            # Check for term matches
            matched_terms = sum(1 for term in query_terms if term in text)
            if matched_terms > 0:
                boost = 1 + (matched_terms / len(query_terms)) * 0.1
                result.relevance_score = min(100, result.relevance_score * boost)
        
        # Re-sort with boosted scores
        semantic_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return semantic_results[:max_results]

