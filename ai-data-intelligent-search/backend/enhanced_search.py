from rapidfuzz import fuzz, process
from typing import List, Dict, Set, Optional
from collections import defaultdict
from models import Person, SearchResult
from scoring_engine import ScoringEngine


class EnhancedSearchEngine:
    """Enhanced search engine with fuzzy matching and efficient indexing"""
    
    def __init__(self, people: List[Person], scoring_engine: ScoringEngine):
        self.people = people
        self.scoring_engine = scoring_engine
        
        # Build indexes for fast lookup
        self.name_index = {}  # firstName + lastName -> [person_ids]
        self.job_title_index = defaultdict(list)  # job_title -> [person_ids]
        self.company_index = defaultdict(list)  # current_company -> [person_ids]
        
        # Build searchable text maps
        self.name_map = {}  # full_name -> person
        self.job_title_map = defaultdict(list)  # job_title -> [persons]
        self.company_map = defaultdict(list)  # company -> [persons]
        
        self._build_indexes()
    
    def _build_indexes(self):
        """Build inverted indexes for fast search"""
        for person in self.people:
            # Name index
            full_name = f"{person.firstName} {person.lastName}".lower()
            self.name_map[full_name] = person
            if full_name not in self.name_index:
                self.name_index[full_name] = []
            self.name_index[full_name].append(person.id)
            
            # Job title index
            if person.job_title:
                job_lower = person.job_title.lower()
                self.job_title_map[job_lower].append(person)
                self.job_title_index[job_lower].append(person.id)
            
            # Company index
            if person.current_company:
                company_lower = person.current_company.lower()
                self.company_map[company_lower].append(person)
                self.company_index[company_lower].append(person.id)
    
    def fuzzy_search_names(self, query: str, limit: int = 10) -> List[Person]:
        """Fuzzy search by name using rapidfuzz"""
        if not query or len(query.strip()) < 2:
            return []
        
        query_lower = query.lower().strip()
        
        # Get all names
        all_names = list(self.name_map.keys())
        
        # Use rapidfuzz for fuzzy matching
        matches = process.extract(
            query_lower,
            all_names,
            scorer=fuzz.partial_ratio,
            limit=limit
        )
        
        # Filter matches with score >= 60
        results = []
        seen_ids = set()
        
        for name, score, _ in matches:
            if score >= 60:
                person = self.name_map[name]
                if person.id not in seen_ids:
                    results.append(person)
                    seen_ids.add(person.id)
        
        return results[:limit]
    
    def fuzzy_search_job_titles(self, query: str, limit: int = 10) -> List[Person]:
        """Fuzzy search by job title"""
        if not query or len(query.strip()) < 2:
            return []
        
        query_lower = query.lower().strip()
        
        # Get all unique job titles
        all_job_titles = list(self.job_title_map.keys())
        
        # Fuzzy match job titles
        matches = process.extract(
            query_lower,
            all_job_titles,
            scorer=fuzz.partial_ratio,
            limit=limit * 2  # Get more to account for multiple people per title
        )
        
        results = []
        seen_ids = set()
        
        for job_title, score, _ in matches:
            if score >= 60:
                persons = self.job_title_map[job_title]
                for person in persons:
                    if person.id not in seen_ids:
                        results.append(person)
                        seen_ids.add(person.id)
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break
        
        return results[:limit]
    
    def fuzzy_search_companies(self, query: str, limit: int = 10) -> List[Person]:
        """Fuzzy search by company name"""
        if not query or len(query.strip()) < 2:
            return []
        
        query_lower = query.lower().strip()
        
        # Get all unique company names
        all_companies = list(self.company_map.keys())
        
        # Fuzzy match company names
        matches = process.extract(
            query_lower,
            all_companies,
            scorer=fuzz.partial_ratio,
            limit=limit * 2  # Get more to account for multiple people per company
        )
        
        results = []
        seen_ids = set()
        
        for company, score, _ in matches:
            if score >= 60:
                persons = self.company_map[company]
                for person in persons:
                    if person.id not in seen_ids:
                        results.append(person)
                        seen_ids.add(person.id)
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break
        
        return results[:limit]
    
    def get_autocomplete_suggestions(self, query: str, max_results: int = 10) -> Dict[str, List[str]]:
        """Get autocomplete suggestions for names, job titles, and companies"""
        if not query or len(query.strip()) < 2:
            return {
                "names": [],
                "job_titles": [],
                "companies": []
            }
        
        query_lower = query.lower().strip()
        
        # Get suggestions for names
        name_suggestions = []
        for name in self.name_map.keys():
            if query_lower in name:
                name_suggestions.append(name.title())
        
        # Get suggestions for job titles
        job_title_suggestions = []
        seen_jobs = set()
        for job_title in self.job_title_map.keys():
            if query_lower in job_title and job_title not in seen_jobs:
                job_title_suggestions.append(job_title.title())
                seen_jobs.add(job_title)
        
        # Get suggestions for companies
        company_suggestions = []
        seen_companies = set()
        for company in self.company_map.keys():
            if query_lower in company and company not in seen_companies:
                company_suggestions.append(company.title())
                seen_companies.add(company)
        
        return {
            "names": name_suggestions[:max_results],
            "job_titles": job_title_suggestions[:max_results],
            "companies": company_suggestions[:max_results]
        }
    
    def search_by_name(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search people by name"""
        persons = self.fuzzy_search_names(query, max_results)
        
        results = []
        for person in persons:
            # Calculate score based on name match
            full_name = f"{person.firstName} {person.lastName}".lower()
            query_lower = query.lower()
            
            # Use fuzzy ratio as score component
            name_score = fuzz.partial_ratio(query_lower, full_name)
            
            # Normalize to 0-100
            normalized_score = min(100, name_score)
            
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, [query_lower], None
            )
            
            # Boost score for name matches
            final_score = max(score, normalized_score * 0.8)
            
            explanation = f"Name match: {person.firstName} {person.lastName}"
            
            results.append(SearchResult(
                person=person,
                relevance_score=round(final_score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
    
    def search_by_job_title(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search people by job title"""
        persons = self.fuzzy_search_job_titles(query, max_results)
        
        results = []
        for person in persons:
            if not person.job_title:
                continue
            
            job_lower = person.job_title.lower()
            query_lower = query.lower()
            
            # Use fuzzy ratio as score component
            job_score = fuzz.partial_ratio(query_lower, job_lower)
            normalized_score = min(100, job_score)
            
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, [query_lower], None
            )
            
            # Boost score for job title matches
            final_score = max(score, normalized_score * 0.8)
            
            explanation = f"Job title match: {person.job_title}"
            
            results.append(SearchResult(
                person=person,
                relevance_score=round(final_score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
    
    def search_by_company(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search people by company"""
        persons = self.fuzzy_search_companies(query, max_results)
        
        results = []
        for person in persons:
            if not person.current_company:
                continue
            
            company_lower = person.current_company.lower()
            query_lower = query.lower()
            
            # Use fuzzy ratio as score component
            company_score = fuzz.partial_ratio(query_lower, company_lower)
            normalized_score = min(100, company_score)
            
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, [query_lower], None
            )
            
            # Boost score for company matches
            final_score = max(score, normalized_score * 0.8)
            
            explanation = f"Company match: {person.current_company}"
            
            results.append(SearchResult(
                person=person,
                relevance_score=round(final_score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]



