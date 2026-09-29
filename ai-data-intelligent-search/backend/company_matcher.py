from typing import List, Optional
from models import Person, Company, SearchResult
from scoring_engine import ScoringEngine


class CompanyMatchmakingEngine:
    """Company-People Matchmaking Engine"""
    
    def __init__(self, people: List[Person], pakistani_companies: List[Company], 
                 scoring_engine: ScoringEngine):
        self.people = people
        self.pakistani_companies = pakistani_companies
        self.scoring_engine = scoring_engine
    
    def extract_company_attributes(self, company: Company) -> dict:
        """Extract key attributes from company for matching"""
        attributes = {
            'industry': company.industry or '',
            'services': company.account_services or '',
            'keywords': company.keywords or '',
            'technologies': company.technologies or '',
            'description': company.account_description or ''
        }
        
        # Combine all text for search terms
        search_text = ' '.join([
            attributes['industry'],
            attributes['services'],
            attributes['keywords'],
            attributes['technologies'],
            attributes['description']
        ]).lower()
        
        # Extract meaningful terms
        terms = [term for term in search_text.split() if len(term) > 3]
        
        return {
            'terms': terms,
            'industry': attributes['industry'],
            'services': attributes['services']
        }
    
    def find_matches(self, company_name: str, target_city: Optional[str] = None, 
                    max_results: int = 5) -> List[SearchResult]:
        """
        Find relevant professionals for a Pakistani IT company
        """
        # Find company
        company = None
        for comp in self.pakistani_companies:
            if (comp.account_name_clean and company_name.lower() in comp.account_name_clean.lower()) or \
               (comp.account_name_profile and company_name.lower() in comp.account_name_profile.lower()):
                company = comp
                break
        
        if not company:
            return []
        
        # Extract company attributes
        company_attrs = self.extract_company_attributes(company)
        search_terms = company_attrs['terms']
        
        # If no terms extracted, use company name and industry
        if not search_terms:
            search_terms = [company.account_name_clean or company.account_name_profile]
            if company.industry:
                search_terms.extend(company.industry.lower().split())
        
        # Score all people
        scored_results = []
        seen_ids = set()
        
        for person in self.people:
            # Skip duplicates
            if person.id in seen_ids:
                continue
            
            # Filter by location if specified
            if target_city:
                if not person.location or target_city.lower() not in person.location.lower():
                    continue
            
            # Calculate score with company context
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, search_terms, target_city, company
            )
            
            # Generate explanation
            explanation = self.scoring_engine.generate_explanation(
                person, breakdown, search_terms, target_city
            )
            
            # Add company-specific context to explanation
            if company.industry and person.industry:
                if company.industry.lower() in person.industry.lower():
                    explanation = f"Expert in {company.industry} industry. {explanation}"
            
            scored_results.append(SearchResult(
                person=person,
                relevance_score=round(score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
            
            seen_ids.add(person.id)
        
        # Sort by relevance score (descending)
        scored_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Return top results
        return scored_results[:max_results]
    
    def generate_matching_criteria(self, company: Company, target_city: Optional[str] = None) -> str:
        """Generate human-readable matching criteria"""
        criteria_parts = []
        
        if company.industry:
            criteria_parts.append(f"Industry: {company.industry}")
        
        if company.account_services:
            criteria_parts.append(f"Services: {company.account_services}")
        
        if target_city:
            criteria_parts.append(f"Location: {target_city}")
        
        return "; ".join(criteria_parts) if criteria_parts else "General matching criteria"

