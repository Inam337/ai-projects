"""
Query Executor
Executes parsed queries against the search engines
"""

from typing import List, Optional, Any
import re
from models import Person, SearchResult, Company
from llm_query_parser import ParsedQuery
from hybrid_search import HybridRetrievalEngine
from company_matcher import CompanyMatchmakingEngine
from data_loader import DataLoader
from rapidfuzz import fuzz


class QueryExecutor:
    """Execute parsed queries against search engines"""
    
    def __init__(self, hybrid_search: HybridRetrievalEngine,
                 company_matcher: CompanyMatchmakingEngine,
                 data_loader: DataLoader,
                 llm_parser: Optional[Any] = None):
        self.hybrid_search = hybrid_search
        self.company_matcher = company_matcher
        self.data_loader = data_loader
        self.llm_parser = llm_parser
    
    def execute(self, parsed_query: ParsedQuery, max_results: int = 10, 
                original_query: str = None) -> List[SearchResult]:
        """
        Execute parsed query and return results
        
        Args:
            parsed_query: Parsed query object
            max_results: Maximum number of results to return
            original_query: Original query string for statistics tracking
            
        Returns:
            List of SearchResult objects
        """
        if parsed_query.query_type == "company_match":
            results = self._execute_company_match(parsed_query, max_results)
        elif parsed_query.query_type == "company_discovery":
            results = self._execute_company_discovery(parsed_query, max_results)
        else:
            results = self._execute_people_search(parsed_query, max_results)
        
        # Record statistics if LLM parser is available
        if self.llm_parser and original_query:
            result_count = len(results)
            avg_relevance = sum(r.relevance_score for r in results) / result_count if result_count > 0 else 0.0
            self.llm_parser.record_query_result(original_query, parsed_query, result_count, avg_relevance)
        
        return results
    
    def _execute_people_search(self, parsed_query: ParsedQuery, max_results: int) -> List[SearchResult]:
        """Execute people search query"""
        # When gender is specified, we need many more candidates because filtering will reduce results significantly
        # Use much larger candidate size to ensure we have enough matching gender results
        candidate_multiplier = 20 if parsed_query.gender else 2  # 20x when gender filter is active
        
        # Use hybrid search with the generated search query
        # Pass gender filter to hybrid_search for early filtering (more efficient)
        # Increase candidate_size significantly when gender filter is active
        candidate_size = 1000 if parsed_query.gender else 200  # Much larger candidate pool for gender filtering
        
        results = self.hybrid_search.hybrid_search(
            parsed_query.search_query or parsed_query.original_query,
            max_results=max_results * candidate_multiplier,  # Get many more candidates for gender filtering
            min_completeness=50.0,
            candidate_size=candidate_size,  # Larger candidate pool when gender filtering
            gender_filter=parsed_query.gender  # Pass gender filter for early filtering
        )
        
        # Debug: Log gender filter status
        if parsed_query.gender:
            print(f"✓ Applying gender filter: '{parsed_query.gender}' - Initial results: {len(results)}")
        
        # Apply filters (gender filter is critical here)
        filtered_results = self._apply_filters(results, parsed_query)
        
        # Debug: Log filtered results
        if parsed_query.gender:
            print(f"✓ After gender filtering: {len(filtered_results)} results (filtered from {len(results)})")
        
        # Re-score filtered results
        rescored_results = self._rescore_results(filtered_results, parsed_query)
        
        # Sort and return top results
        rescored_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return rescored_results[:max_results]
    
    def _execute_company_match(self, parsed_query: ParsedQuery, max_results: int) -> List[SearchResult]:
        """Execute company match query (Objective 2A)"""
        if not parsed_query.pakistani_company:
            # Fallback to people search
            return self._execute_people_search(parsed_query, max_results)
        
        # Find Pakistani company
        pakistani_company = self.data_loader.get_pakistani_company_by_name(
            parsed_query.pakistani_company
        )
        
        if not pakistani_company:
            # Company not found, use search query instead
            return self._execute_people_search(parsed_query, max_results)
        
        # Extract target location from visit context or locations
        target_city = None
        if parsed_query.visit_context:
            if 'riyadh' in parsed_query.visit_context.lower():
                target_city = "Riyadh"
            elif 'jeddah' in parsed_query.visit_context.lower():
                target_city = "Jeddah"
            elif 'ksa' in parsed_query.visit_context.lower() or 'saudi' in parsed_query.visit_context.lower():
                # For KSA/Saudi Arabia, don't specify city (search all of Saudi Arabia)
                target_city = None  # Will search all Saudi locations
        
        if not target_city and parsed_query.locations:
            # Check if location is KSA/Saudi Arabia
            location_lower = parsed_query.locations[0].lower()
            if 'ksa' in location_lower or 'saudi' in location_lower:
                # For KSA, don't restrict to a specific city
                target_city = None
            else:
                target_city = parsed_query.locations[0].capitalize()
        
        # Use company matcher
        results = self.company_matcher.find_matches(
            pakistani_company.account_name_profile or pakistani_company.account_name_clean,
            target_city=target_city,
            max_results=max_results * 2
        )
        
        # Apply additional filters
        filtered_results = self._apply_filters(results, parsed_query)
        
        # Re-score with parsed query context
        rescored_results = self._rescore_results(filtered_results, parsed_query)
        
        rescored_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return rescored_results[:max_results]
    
    def _execute_company_discovery(self, parsed_query: ParsedQuery, max_results: int) -> List[SearchResult]:
        """Execute company discovery query (Objective 2B/C)"""
        # For company discovery, we search for Pakistani companies
        # This is a simplified version - can be enhanced
        companies = self.data_loader.pakistani_companies
        
        # Filter companies based on query
        filtered_companies = []
        query_lower = parsed_query.original_query.lower()
        
        for company in companies:
            score = 0.0
            company_text = company.get_searchable_text().lower()
            
            # Match industries
            for industry in parsed_query.industries:
                if industry in company_text:
                    score += 10
            
            # Match technologies
            for tech in parsed_query.technologies:
                if tech in company_text:
                    score += 10
            
            # Match keywords
            for keyword in parsed_query.keywords:
                if keyword in company_text:
                    score += 5
            
            if score > 0:
                filtered_companies.append((company, score))
        
        # Sort by score
        filtered_companies.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to SearchResult format (simplified - companies don't have Person objects)
        # For now, return empty or use people search as fallback
        return self._execute_people_search(parsed_query, max_results)
    
    def _apply_filters(self, results: List[SearchResult], parsed_query: ParsedQuery) -> List[SearchResult]:
        """Apply filters to search results with strict gender and country prioritization"""
        filtered = []
        
        # Extract country from locations if present
        target_country = None
        if parsed_query.locations:
            location_lower = " ".join(parsed_query.locations).lower()
            if 'saudi' in location_lower or 'ksa' in location_lower:
                target_country = 'saudi arabia'
            elif 'pakistan' in location_lower or 'pakistani' in location_lower:
                target_country = 'pakistan'
        
        for result in results:
            person = result.person
            
            # Strict gender filter - if gender is specified, ONLY show that gender
            # When gender is NOT specified (None), show all genders (no filtering)
            if parsed_query.gender:
                # Normalize gender values - handle various formats
                query_gender = parsed_query.gender.lower().strip()
                
                # Normalize person gender - handle various formats and abbreviations
                person_gender_raw = person.gender
                if not person_gender_raw:
                    continue  # Exclude if no gender data
                
                person_gender = str(person_gender_raw).lower().strip()
                
                # Gender normalization mapping (handle 'f', 'm', 'female', 'male', etc.)
                gender_normalization = {
                    'f': 'female', 'female': 'female', 'females': 'female',
                    'm': 'male', 'male': 'male', 'males': 'male'
                }
                
                query_gender_normalized = gender_normalization.get(query_gender, query_gender)
                person_gender_normalized = gender_normalization.get(person_gender, person_gender)
                
                # Only include if genders match exactly after normalization
                if person_gender_normalized != query_gender_normalized:
                    continue  # Exclude non-matching genders
                
                # Debug: Log first few matches for verification
                if len(filtered) < 3:
                    print(f"  ✓ Gender match: {person.firstName} {person.lastName} - person.gender='{person_gender_raw}' -> normalized='{person_gender_normalized}'")
            
            # Premium filter
            if parsed_query.premium_only:
                if not person.premium or person.premium.lower() != 'yes':
                    continue
            
            # Location/Country filter - prioritize exact country matches
            if parsed_query.locations or target_country:
                person_location = (person.location or "").lower()
                person_country = (person.account_country or "").lower()
                person_city = (person.account_city or "").lower()
                
                # Check for country match first (highest priority)
                if target_country:
                    country_match = target_country.lower() in person_country or target_country.lower() in person_location
                    if not country_match:
                        # Also check location field for country
                        if 'saudi' in target_country.lower():
                            if 'saudi' not in person_location and 'ksa' not in person_location and 'saudi' not in person_country:
                                continue
                        elif 'pakistan' in target_country.lower():
                            if 'pakistan' not in person_location and 'pakistani' not in person_location and 'pakistan' not in person_country:
                                continue
                
                # Check for city/location match
                if parsed_query.locations:
                    location_match = False
                    
                    for loc in parsed_query.locations:
                        loc_lower = loc.lower()
                        
                        # Check for KSA/Saudi Arabia match (should match any Saudi location)
                        if loc_lower in ['ksa', 'saudi', 'saudi arabia']:
                            if ('saudi' in person_location or 'ksa' in person_location or 
                                'saudi' in person_country or 'ksa' in person_country or
                                'riyadh' in person_location or 'jeddah' in person_location or
                                'riyadh' in person_city or 'jeddah' in person_city):
                                location_match = True
                                break
                        # Check for specific city/location match
                        elif (loc_lower in person_location or loc_lower in person_city or 
                              loc_lower in (person.account_state or "").lower() or 
                              loc_lower in person_country):
                            location_match = True
                            break
                    
                    if not location_match:
                        continue
            
            # Company filter
            if parsed_query.companies:
                person_company = (person.current_company or "").lower()
                account_name = (person.account_name_profile or "").lower()
                if not any(comp.lower() in person_company or comp.lower() in account_name 
                          for comp in parsed_query.companies):
                    continue
            
            # Company type filter (OR logic - match any company type)
            if parsed_query.company_types:
                person_company = (person.current_company or "").lower()
                account_name = (person.account_name_profile or "").lower()
                company_text = f"{person_company} {account_name}".lower()
                
                # Check if any company type matches (OR logic)
                type_match = False
                for company_type in parsed_query.company_types:
                    if company_type == 'government' and any(word in company_text 
                        for word in ['government', 'ministry', 'public sector', 'public-sector']):
                        type_match = True
                        break
                    elif company_type == 'banks' and 'bank' in company_text:
                        type_match = True
                        break
                    elif company_type == 'startups' and 'startup' in company_text:
                        type_match = True
                        break
                    elif company_type == 'healthcare' and any(word in company_text 
                        for word in ['hospital', 'healthcare', 'medical', 'health']):
                        type_match = True
                        break
                    elif company_type == 'telecom' and any(word in company_text 
                        for word in ['telecom', 'telecommunications', 'mobile operator']):
                        type_match = True
                        break
                    elif company_type == 'retail' and any(word in company_text 
                        for word in ['retail', 'ecommerce', 'e-commerce']):
                        type_match = True
                        break
                    elif company_type == 'tech' and any(word in company_text 
                        for word in ['tech', 'technology', 'software', 'it']):
                        type_match = True
                        break
                    elif company_type == 'enterprises' and any(word in company_text 
                        for word in ['enterprise', 'enterprises', 'large company', 'corporation']):
                        type_match = True
                        break
                    elif company_type == 'facility_management' and 'facility management' in company_text:
                        type_match = True
                        break
                    elif company_type == 'logistics' and 'logistics' in company_text:
                        type_match = True
                        break
                    elif company_type == 'energy' and any(word in company_text 
                        for word in ['energy', 'oil', 'gas', 'petroleum', 'utilities']):
                        type_match = True
                        break
                    elif company_type == 'construction' and any(word in company_text 
                        for word in ['construction', 'infrastructure']):
                        type_match = True
                        break
                
                if not type_match:
                    continue
            
            # Job title filter (OR logic - match any job title, fuzzy match)
            if parsed_query.job_titles:
                person_job = (person.job_title or "").lower()
                person_headline = (person.headline or "").lower()
                job_text = f"{person_job} {person_headline}".lower()
                
                title_match = False
                for title in parsed_query.job_titles:
                    title_lower = title.lower()
                    # Exact match
                    if title_lower in job_text:
                        title_match = True
                        break
                    # Check if title is part of compound phrase (e.g., "data analytics" in "data analytics leader")
                    if title_lower in job_text or any(word in job_text for word in title_lower.split()):
                        title_match = True
                        break
                    # Fuzzy match
                    if person_job:
                        similarity = fuzz.partial_ratio(title_lower, person_job)
                        if similarity >= 70:
                            title_match = True
                            break
                
                if not title_match:
                    continue
            
            # Revenue range filter
            if parsed_query.revenue_range:
                # Extract revenue from person's company
                person_revenue = (person.annual_revenue or "").lower()
                if not person_revenue:
                    continue  # Skip if no revenue data
                
                # Parse revenue range (e.g., "$10-50M")
                range_match = re.search(r'\$?(\d+)[–-](\d+)M?', parsed_query.revenue_range)
                if range_match:
                    min_revenue = int(range_match.group(1))
                    max_revenue = int(range_match.group(2))
                    
                    # Extract person's revenue (handle various formats)
                    person_revenue_match = re.search(r'(\d+)', person_revenue.replace(',', ''))
                    if person_revenue_match:
                        person_revenue_val = int(person_revenue_match.group(1))
                        # Check if in range (simplified - assumes millions)
                        if not (min_revenue <= person_revenue_val <= max_revenue):
                            continue
            
            # Funding filter
            if parsed_query.has_funding is not None or parsed_query.recently_raised_funding:
                # This would require additional data fields - for now, skip if funding is required
                # In the future, this could check company funding status
                pass
            
            filtered.append(result)
        
        return filtered
    
    def _rescore_results(self, results: List[SearchResult], parsed_query: ParsedQuery) -> List[SearchResult]:
        """Re-score results based on parsed query parameters with top-5 formula"""
        from scoring_engine import ScoringEngine
        
        rescored = []
        scoring_engine = ScoringEngine()
        
        # Extract query terms from search query
        query_terms = parsed_query.search_query.split() if parsed_query.search_query else []
        query_location = parsed_query.locations[0] if parsed_query.locations else None
        
        for rank, result in enumerate(results, 1):
            person = result.person
            
            # Use top-5 scoring formula for first 5 results
            if rank <= 5:
                final_score, breakdown = scoring_engine.calculate_top5_score(
                    person=person,
                    query_terms=query_terms,
                    query_location=query_location,
                    company=None,
                    seniority_levels=parsed_query.seniority_levels,
                    rank=rank,
                    query_gender=parsed_query.gender
                )
            else:
                # Use standard scoring for results beyond top 5
                final_score, breakdown = scoring_engine.calculate_total_score(
                    person=person,
                    query_terms=query_terms,
                    query_location=query_location,
                    company=None,
                    seniority_levels=parsed_query.seniority_levels,
                    query_gender=parsed_query.gender
                )
            
            # Additional exact match boosts with priority for gender and country
            boost = 0.0
            
            # Gender match boost (HIGH PRIORITY - significant boost)
            if parsed_query.gender and person.gender:
                if person.gender.lower() == parsed_query.gender.lower():
                    boost += 15.0  # Large boost for gender match
            
            # Country match boost (HIGH PRIORITY - significant boost)
            target_country = None
            if parsed_query.locations:
                location_lower = " ".join(parsed_query.locations).lower()
                if 'saudi' in location_lower or 'ksa' in location_lower:
                    target_country = 'saudi arabia'
                elif 'pakistan' in location_lower or 'pakistani' in location_lower:
                    target_country = 'pakistan'
            
            if target_country:
                person_location = (person.location or "").lower()
                person_country = (person.account_country or "").lower()
                if target_country.lower() in person_country or target_country.lower() in person_location:
                    boost += 15.0  # Large boost for country match
                elif 'saudi' in target_country.lower() and ('saudi' in person_location or 'ksa' in person_location):
                    boost += 15.0
                elif 'pakistan' in target_country.lower() and ('pakistan' in person_location or 'pakistani' in person_location):
                    boost += 15.0
            
            # Job title exact match boost
            if parsed_query.job_titles:
                person_job = (person.job_title or "").lower()
                person_headline = (person.headline or "").lower()
                person_text = f"{person_job} {person_headline}".lower()
                for title in parsed_query.job_titles:
                    if title.lower() in person_text:
                        boost += 3.0
                        break
            
            # Company exact match boost
            if parsed_query.companies:
                person_company = (person.current_company or "").lower()
                account_name = (person.account_name_profile or "").lower()
                for comp in parsed_query.companies:
                    if comp.lower() in person_company or comp.lower() in account_name:
                        boost += 3.0
                        break
            
            # Location exact match boost
            if parsed_query.locations:
                person_location = (person.location or "").lower()
                account_city = (person.account_city or "").lower()
                for loc in parsed_query.locations:
                    if loc.lower() in person_location or loc.lower() in account_city:
                        boost += 2.0
                        break
            
            # Industry/Technology match boost
            if parsed_query.industries or parsed_query.technologies:
                person_text = person.get_searchable_text()
                for term in parsed_query.industries + parsed_query.technologies:
                    if term.lower() in person_text:
                        boost += 2.0
                        break
            
            # Apply boost (capped at 100)
            final_score = min(100.0, final_score + boost)
            
            # Generate explanation
            explanation = scoring_engine.generate_explanation(
                person, breakdown, query_terms, query_location
            )
            
            # Add gender match info to explanation
            if parsed_query.gender and person.gender:
                if person.gender.lower() == parsed_query.gender.lower():
                    explanation = f"Gender match ({person.gender}). {explanation}"
            
            # Add country match info to explanation
            if target_country:
                person_location = (person.location or "").lower()
                person_country = (person.account_country or "").lower()
                if target_country.lower() in person_country or target_country.lower() in person_location:
                    explanation = f"Country match ({target_country.title()}). {explanation}"
                elif 'saudi' in target_country.lower() and ('saudi' in person_location or 'ksa' in person_location):
                    explanation = f"Country match (Saudi Arabia). {explanation}"
                elif 'pakistan' in target_country.lower() and ('pakistan' in person_location or 'pakistani' in person_location):
                    explanation = f"Country match (Pakistan). {explanation}"
            
            # Add seniority info to explanation if matched
            if parsed_query.seniority_levels and person.seniority:
                person_seniority = person.seniority.lower()
                for level in parsed_query.seniority_levels:
                    if level.lower() in person_seniority or level.lower() in (person.job_title or "").lower():
                        explanation = f"Seniority match ({person.seniority}). {explanation}"
                        break
            
            # Create new result with rescored values
            new_result = SearchResult(
                person=result.person,
                relevance_score=round(final_score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            )
            rescored.append(new_result)
        
        return rescored

