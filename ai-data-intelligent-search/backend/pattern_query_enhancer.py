"""
Pattern-based Query Enhancer for Vector Search
Enhances queries with regex pattern matching to improve search accuracy
"""

import re
from typing import List, Dict, Tuple, Optional


class PatternQueryEnhancer:
    """Enhance queries with pattern-based matching for better vector search results"""
    
    def __init__(self):
        # Job title patterns
        self.job_patterns = {
            'developer': ['developer', 'dev', 'programmer', 'coder', 'software engineer', 'software developer'],
            'engineer': ['engineer', 'engineering', 'eng'],
            'manager': ['manager', 'management', 'mgr'],
            'director': ['director', 'directors'],
            'executive': ['executive', 'exec', 'executives'],
            'lead': ['lead', 'leader', 'leaders', 'leading'],
            'architect': ['architect', 'architecture'],
            'analyst': ['analyst', 'analysis', 'analytics'],
            'consultant': ['consultant', 'consulting'],
            'specialist': ['specialist', 'specialists'],
            'ceo': ['ceo', 'chief executive', 'chief executive officer'],
            'cto': ['cto', 'chief technology', 'chief tech officer'],
            'cio': ['cio', 'chief information', 'chief information officer'],
            'cdo': ['cdo', 'chief data', 'chief data officer'],
        }
        
        # Location patterns
        self.location_patterns = {
            'ksa': ['ksa', 'saudi arabia', 'saudi', 'kingdom of saudi arabia'],
            'riyadh': ['riyadh', 'riyad'],
            'jeddah': ['jeddah', 'jiddah'],
            'dammam': ['dammam', 'damam'],
            'pakistan': ['pakistan', 'pakistani'],
            'karachi': ['karachi'],
            'lahore': ['lahore'],
            'islamabad': ['islamabad'],
        }
        
        # Quantity patterns
        self.quantity_patterns = {
            'all': ['all', 'every', 'entire'],
            'top': ['top', 'best', 'leading'],
            'some': ['some', 'few', 'several'],
            'many': ['many', 'multiple', 'numerous'],
        }
        
        # Natural language query patterns
        self.query_patterns = {
            'list': r'\b(list|show|display|find|get|give me|show me)\s+(?:me\s+)?(?:all\s+)?(?:of\s+)?(?:the\s+)?',
            'all_of': r'\b(all|every|entire)\s+(?:of\s+)?(?:the\s+)?',
            'in_location': r'\bin\s+([a-z\s]+?)(?:\s+working|\s+at|\s+for|$)',
            'working': r'\bworking\s+(?:on|at|in|for)\s+([a-z\s]+?)(?:\s+in|\s+at|$)',
        }
    
    def enhance_query(self, query: str) -> Dict[str, any]:
        """
        Enhance query with pattern matching and extract structured information
        
        Returns:
            Dictionary with enhanced query and extracted patterns
        """
        query_lower = query.lower()
        
        # Extract job titles
        extracted_jobs = self._extract_job_titles(query_lower)
        
        # Extract locations
        extracted_locations = self._extract_locations(query_lower)
        
        # Extract quantity modifiers
        quantity_modifier = self._extract_quantity(query_lower)
        
        # Build enhanced query
        enhanced_terms = []
        
        # Add job titles
        if extracted_jobs:
            enhanced_terms.extend(extracted_jobs)
        
        # Add locations
        if extracted_locations:
            enhanced_terms.extend(extracted_locations)
        
        # Add original query terms (filtered)
        original_terms = self._extract_meaningful_terms(query_lower)
        enhanced_terms.extend(original_terms)
        
        # Build enhanced query string
        enhanced_query = " ".join(enhanced_terms) if enhanced_terms else query
        
        return {
            'original_query': query,
            'enhanced_query': enhanced_query,
            'job_titles': extracted_jobs,
            'locations': extracted_locations,
            'quantity_modifier': quantity_modifier,
            'patterns_matched': {
                'has_list_pattern': bool(re.search(self.query_patterns['list'], query_lower)),
                'has_all_pattern': bool(re.search(self.query_patterns['all_of'], query_lower)),
                'has_location': len(extracted_locations) > 0,
                'has_job_title': len(extracted_jobs) > 0,
            }
        }
    
    def _extract_job_titles(self, query_lower: str) -> List[str]:
        """Extract job titles from query using pattern matching"""
        found_jobs = []
        
        for job_key, patterns in self.job_patterns.items():
            for pattern in patterns:
                # Use word boundaries for exact matching
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower, re.IGNORECASE):
                    if job_key not in found_jobs:
                        found_jobs.append(job_key)
                    break
        
        return found_jobs
    
    def _extract_locations(self, query_lower: str) -> List[str]:
        """Extract locations from query using pattern matching"""
        found_locations = []
        
        for loc_key, patterns in self.location_patterns.items():
            for pattern in patterns:
                # Use word boundaries for exact matching
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower, re.IGNORECASE):
                    if loc_key not in found_locations:
                        found_locations.append(loc_key)
                    break
        
        return found_locations
    
    def _extract_quantity(self, query_lower: str) -> Optional[str]:
        """Extract quantity modifier from query"""
        for qty_key, patterns in self.quantity_patterns.items():
            for pattern in patterns:
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower, re.IGNORECASE):
                    return qty_key
        return None
    
    def _extract_meaningful_terms(self, query_lower: str) -> List[str]:
        """Extract meaningful terms from query, filtering out stop words"""
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must',
            'who', 'are', 'find', 'show', 'me', 'list', 'of', 'give', 'us', 'tell', 'get',
            'working', 'work', 'works', 'worked', 'that', 'this', 'these', 'those',
            'which', 'what', 'where', 'when', 'why', 'how', 'there', 'their', 'they', 'them'
        }
        
        words = re.findall(r'\b\w+\b', query_lower)
        meaningful_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return meaningful_terms
    
    def match_patterns(self, query: str) -> Dict[str, bool]:
        """Check which patterns match in the query"""
        query_lower = query.lower()
        matches = {}
        
        for pattern_name, pattern_regex in self.query_patterns.items():
            matches[pattern_name] = bool(re.search(pattern_regex, query_lower, re.IGNORECASE))
        
        return matches

