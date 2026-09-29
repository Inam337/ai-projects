"""
Query Vector Store
Stores parsed queries as vectors for similarity matching and statistics tracking
"""

import json
import os
import pickle
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

# Lazy import of sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

# Lazy import of FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None


class QueryStats:
    """Statistics for a query"""
    def __init__(self, query: str, parsed_query: Dict):
        self.query = query
        self.parsed_query = parsed_query
        self.timestamp = datetime.now().isoformat()
        self.count = 1
        self.last_used = datetime.now().isoformat()
        self.result_count = 0
        self.avg_relevance_score = 0.0
        
    def to_dict(self):
        return {
            'query': self.query,
            'parsed_query': self.parsed_query,
            'timestamp': self.timestamp,
            'count': self.count,
            'last_used': self.last_used,
            'result_count': self.result_count,
            'avg_relevance_score': self.avg_relevance_score
        }


class QueryVectorStore:
    """Vector database for storing and retrieving similar queries"""
    
    def __init__(self, store_dir: str = "query_store"):
        """
        Initialize Query Vector Store
        
        Args:
            store_dir: Directory to store query vectors and statistics
        """
        self.store_dir = store_dir
        os.makedirs(store_dir, exist_ok=True)
        
        # Initialize embedding model if available
        self.embedding_model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
        
        # Initialize FAISS index if available
        self.index = None
        self.query_stats: Dict[str, QueryStats] = {}
        self.idx_to_query: Dict[int, str] = {}
        self.query_to_idx: Dict[str, int] = {}
        self.next_idx = 0
        
        # File paths
        self.stats_file = os.path.join(store_dir, "query_stats.json")
        self.index_file = os.path.join(store_dir, "query_index.bin")
        self.mapping_file = os.path.join(store_dir, "query_mapping.pkl")
        
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing data or initialize new store"""
        # Load statistics
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats_data = json.load(f)
                    for query, stats_dict in stats_data.items():
                        stats = QueryStats(stats_dict['query'], stats_dict['parsed_query'])
                        stats.count = stats_dict.get('count', 1)
                        stats.last_used = stats_dict.get('last_used', stats.timestamp)
                        stats.result_count = stats_dict.get('result_count', 0)
                        stats.avg_relevance_score = stats_dict.get('avg_relevance_score', 0.0)
                        self.query_stats[query] = stats
                print(f"Loaded {len(self.query_stats)} query statistics")
            except Exception as e:
                print(f"Error loading query stats: {e}")
        
        # Load FAISS index if available
        if FAISS_AVAILABLE and faiss and self.embedding_model:
            if os.path.exists(self.index_file) and os.path.exists(self.mapping_file):
                try:
                    self.index = faiss.read_index(self.index_file)
                    with open(self.mapping_file, 'rb') as f:
                        self.query_to_idx = pickle.load(f)
                    self.idx_to_query = {v: k for k, v in self.query_to_idx.items()}
                    self.next_idx = len(self.query_to_idx)
                    print(f"Loaded query vector index with {self.index.ntotal} vectors")
                except Exception as e:
                    print(f"Error loading query index: {e}")
                    self._initialize_index()
            else:
                self._initialize_index()
    
    def _initialize_index(self):
        """Initialize new FAISS index"""
        if FAISS_AVAILABLE and faiss and self.embedding_model:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            # Normalize for cosine similarity
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            print("Initialized new query vector index")
    
    def _get_query_text(self, query: str, parsed_query: Dict) -> str:
        """Create text representation of query for embedding"""
        parts = [query]
        
        # Add parsed components
        if parsed_query.get('job_titles'):
            parts.extend(parsed_query['job_titles'])
        if parsed_query.get('industries'):
            parts.extend(parsed_query['industries'])
        if parsed_query.get('technologies'):
            parts.extend(parsed_query['technologies'])
        if parsed_query.get('locations'):
            parts.extend(parsed_query['locations'])
        if parsed_query.get('keywords'):
            parts.extend(parsed_query['keywords'])
        if parsed_query.get('pakistani_company'):
            parts.append(parsed_query['pakistani_company'])
        if parsed_query.get('target_sector'):
            parts.append(parsed_query['target_sector'])
        
        return " ".join(parts)
    
    def add_query(self, query: str, parsed_query: Dict, result_count: int = 0, 
                  avg_relevance: float = 0.0):
        """
        Add or update a query in the store
        
        Args:
            query: Original query string
            parsed_query: Parsed query dictionary
            result_count: Number of results returned
            avg_relevance: Average relevance score of results
        """
        query_lower = query.lower().strip()
        
        # Update statistics
        if query_lower in self.query_stats:
            stats = self.query_stats[query_lower]
            stats.count += 1
            stats.last_used = datetime.now().isoformat()
            stats.result_count = result_count
            stats.avg_relevance_score = avg_relevance
        else:
            stats = QueryStats(query, parsed_query)
            stats.result_count = result_count
            stats.avg_relevance_score = avg_relevance
            self.query_stats[query_lower] = stats
        
        # Add to vector index if available
        if self.embedding_model and self.index is not None and FAISS_AVAILABLE:
            query_text = self._get_query_text(query, parsed_query)
            
            if query_lower not in self.query_to_idx:
                # New query - add to index
                embedding = self.embedding_model.encode([query_text])
                embedding = np.array(embedding).astype('float32')
                faiss.normalize_L2(embedding)
                
                idx = self.next_idx
                self.index.add(embedding)
                self.query_to_idx[query_lower] = idx
                self.idx_to_query[idx] = query_lower
                self.next_idx += 1
            # Existing query - index already has it
        
        self._save()
    
    def find_similar_queries(self, query: str, parsed_query: Dict, 
                             top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar queries using vector similarity
        
        Args:
            query: Query string
            parsed_query: Parsed query dictionary
            top_k: Number of similar queries to return
            
        Returns:
            List of (query, similarity_score) tuples
        """
        if not self.embedding_model or self.index is None or self.index.ntotal == 0:
            return []
        
        query_text = self._get_query_text(query, parsed_query)
        query_embedding = self.embedding_model.encode([query_text])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        k = min(top_k, self.index.ntotal)
        similarities, indices = self.index.search(query_embedding, k)
        
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx == -1:
                continue
            similar_query = self.idx_to_query.get(idx)
            if similar_query and similar_query != query.lower().strip():
                # Convert inner product to similarity score (0-1)
                similarity_score = float(max(0, min(1, sim)))
                results.append((similar_query, similarity_score))
        
        return results
    
    def get_query_stats(self, query: str) -> Optional[QueryStats]:
        """Get statistics for a query"""
        return self.query_stats.get(query.lower().strip())
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """Get most popular queries by count"""
        sorted_queries = sorted(
            self.query_stats.items(),
            key=lambda x: x[1].count,
            reverse=True
        )
        return [stats.to_dict() for _, stats in sorted_queries[:limit]]
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get most recently used queries"""
        sorted_queries = sorted(
            self.query_stats.items(),
            key=lambda x: x[1].last_used,
            reverse=True
        )
        return [stats.to_dict() for _, stats in sorted_queries[:limit]]
    
    def optimize_search_query(self, query: str, parsed_query: Dict) -> str:
        """
        Optimize search query using similar queries and statistics
        
        Args:
            query: Original query
            parsed_query: Parsed query dictionary
            
        Returns:
            Optimized search query string
        """
        # Start with original search query
        optimized = parsed_query.get('search_query', query)
        
        # Find similar queries
        similar_queries = self.find_similar_queries(query, parsed_query, top_k=3)
        
        # If we have similar queries with good results, enhance the query
        for similar_query, similarity in similar_queries:
            if similarity > 0.7:  # High similarity threshold
                stats = self.get_query_stats(similar_query)
                if stats and stats.avg_relevance_score > 70:  # Good results
                    # Add terms from successful similar query
                    similar_parsed = stats.parsed_query
                    additional_terms = []
                    
                    if similar_parsed.get('keywords'):
                        additional_terms.extend(similar_parsed['keywords'])
                    if similar_parsed.get('technologies'):
                        additional_terms.extend(similar_parsed['technologies'])
                    
                    if additional_terms:
                        optimized = f"{optimized} {' '.join(additional_terms[:3])}"
        
        return optimized.strip()
    
    def _save(self):
        """Save statistics and index to disk"""
        # Save statistics
        try:
            stats_dict = {q: s.to_dict() for q, s in self.query_stats.items()}
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving query stats: {e}")
        
        # Save FAISS index
        if self.index is not None and FAISS_AVAILABLE:
            try:
                faiss.write_index(self.index, self.index_file)
                with open(self.mapping_file, 'wb') as f:
                    pickle.dump(self.query_to_idx, f)
            except Exception as e:
                print(f"Error saving query index: {e}")
    
    def get_statistics_summary(self) -> Dict:
        """Get overall statistics summary"""
        total_queries = len(self.query_stats)
        total_searches = sum(s.count for s in self.query_stats.values())
        avg_results = sum(s.result_count for s in self.query_stats.values()) / total_queries if total_queries > 0 else 0
        avg_relevance = sum(s.avg_relevance_score for s in self.query_stats.values()) / total_queries if total_queries > 0 else 0
        
        return {
            'total_unique_queries': total_queries,
            'total_searches': total_searches,
            'avg_results_per_query': round(avg_results, 2),
            'avg_relevance_score': round(avg_relevance, 2),
            'vector_index_size': self.index.ntotal if self.index else 0
        }

