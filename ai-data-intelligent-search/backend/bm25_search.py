"""
BM25 Lexical Search Implementation
Phase 3: Hybrid Retrieval Pipeline - First Stage (Lexical/BM25)

This module implements BM25 ranking algorithm for fast lexical retrieval.
No external dependencies - pure Python implementation.
"""

import math
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from models import Person


class BM25SearchEngine:
    """
    BM25 (Best Matching 25) lexical search engine
    Pure Python implementation - no external dependencies
    """
    
    def __init__(self, people: List[Person], k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 search engine
        
        Args:
            people: List of Person objects to index
            k1: Term frequency saturation parameter (default 1.5)
            b: Length normalization parameter (default 0.75)
        """
        self.people = people
        self.k1 = k1
        self.b = b
        
        # Document frequency for each term
        self.df: Dict[str, int] = defaultdict(int)
        
        # Term frequency per document
        self.tf: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Document lengths
        self.doc_lengths: Dict[str, int] = {}
        
        # Inverted index: term -> set of person IDs
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Average document length
        self.avg_doc_length = 0.0
        
        # Total number of documents
        self.num_docs = len(people)
        
        self._build_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms"""
        if not text:
            return []
        
        # Simple tokenization: lowercase, split on whitespace and punctuation
        import re
        # Remove punctuation and split
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Filter out very short tokens
        return [t for t in tokens if len(t) > 2]
    
    def _get_document_text(self, person: Person) -> str:
        """Extract searchable text from person profile"""
        parts = [
            person.firstName or "",
            person.lastName or "",
            person.job_title or "",
            person.headline or "",
            person.location or "",
            person.current_company or "",
            person.industry or "",
            person.seniority or "",
        ]
        return " ".join(parts)
    
    def _build_index(self):
        """Build BM25 inverted index"""
        total_length = 0
        
        for person in self.people:
            person_id = person.id
            doc_text = self._get_document_text(person)
            tokens = self._tokenize(doc_text)
            
            # Store document length
            doc_length = len(tokens)
            self.doc_lengths[person_id] = doc_length
            total_length += doc_length
            
            # Build term frequency and inverted index
            term_counts = defaultdict(int)
            for token in tokens:
                term_counts[token] += 1
                self.inverted_index[token].add(person_id)
            
            # Store term frequencies for this document
            for term, count in term_counts.items():
                self.tf[person_id][term] = count
                self.df[term] += 1
        
        # Calculate average document length
        if self.num_docs > 0:
            self.avg_doc_length = total_length / self.num_docs
    
    def _idf(self, term: str) -> float:
        """
        Calculate Inverse Document Frequency (IDF) for a term
        
        IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5))
        where N is total number of documents
        """
        if term not in self.df or self.df[term] == 0:
            return 0.0
        
        # Using BM25 IDF formula
        numerator = self.num_docs - self.df[term] + 0.5
        denominator = self.df[term] + 0.5
        
        return math.log(numerator / denominator)
    
    def _bm25_score(self, person_id: str, query_terms: List[str]) -> float:
        """
        Calculate BM25 score for a document given query terms
        
        BM25(q, d) = sum(IDF(t) * (tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * |d|/avgdl)))
        """
        score = 0.0
        
        if person_id not in self.doc_lengths:
            return 0.0
        
        doc_length = self.doc_lengths[person_id]
        
        for term in query_terms:
            if term not in self.inverted_index:
                continue
            
            if person_id not in self.inverted_index[term]:
                continue
            
            # Term frequency in document
            tf = self.tf[person_id].get(term, 0)
            
            if tf == 0:
                continue
            
            # Inverse document frequency
            idf = self._idf(term)
            
            # Length normalization factor
            length_norm = 1 - self.b + self.b * (doc_length / self.avg_doc_length)
            
            # BM25 component for this term
            term_score = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * length_norm)
            
            score += term_score
        
        return score
    
    def search(self, query: str, max_results: int = 200) -> List[Tuple[Person, float]]:
        """
        Perform BM25 lexical search
        
        Args:
            query: Search query string
            max_results: Maximum number of candidate results to return
        
        Returns:
            List of (Person, BM25_score) tuples, sorted by score descending
        """
        if not query or not query.strip():
            return []
        
        # Tokenize query
        query_terms = self._tokenize(query)
        
        if not query_terms:
            return []
        
        # Get candidate documents (union of all terms)
        candidate_ids = set()
        for term in query_terms:
            if term in self.inverted_index:
                candidate_ids.update(self.inverted_index[term])
        
        if not candidate_ids:
            return []
        
        # Score all candidates
        scored_results = []
        person_map = {p.id: p for p in self.people}
        
        for person_id in candidate_ids:
            if person_id not in person_map:
                continue
            
            score = self._bm25_score(person_id, query_terms)
            
            if score > 0:
                person = person_map[person_id]
                scored_results.append((person, score))
        
        # Sort by score descending
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top candidates
        return scored_results[:max_results]
    
    def get_candidate_set(self, query: str, max_candidates: int = 200) -> List[Person]:
        """
        Get candidate set for hybrid retrieval pipeline
        
        Returns:
            List of Person objects ranked by BM25 score
        """
        results = self.search(query, max_candidates)
        return [person for person, score in results]




