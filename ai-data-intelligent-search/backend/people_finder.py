import re
from typing import List, Set, Optional
from models import Person, Company, SearchResult
from scoring_engine import ScoringEngine


class PeopleFinderEngine:
    """Private People Finder Engine - handles natural language queries"""
    
    def __init__(self, people: List[Person], scoring_engine: ScoringEngine):
        self.people = people
        self.scoring_engine = scoring_engine
    
    def extract_query_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from natural language query"""
        # Extended stop words including natural language query patterns
        stop_words = {
            # Basic stop words
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
            # Natural language query starters/modifiers
            'who', 'are', 'find', 'show', 'me', 'list', 'of', 'give', 'us', 'tell', 'get',
            'working', 'work', 'works', 'worked', 'working on', 'working at', 'working in',
            'that', 'this', 'these', 'those', 'which', 'what', 'where', 'when', 'why', 'how',
            'there', 'their', 'they', 'them', 'then', 'than', 'from', 'as', 'if', 'it', 'its',
            # Common query connectors
            'such', 'like', 'other', 'others', 'some', 'many', 'most', 'more', 'all', 'any',
            'also', 'too', 'very', 'just', 'only', 'even', 'still', 'yet', 'already',
            # Question words and modifiers
            'about', 'above', 'below', 'after', 'before', 'during', 'while', 'until', 'since',
            'here', 'there', 'where', 'everywhere', 'somewhere', 'anywhere', 'nowhere'
        }
        
        # Convert to lowercase and split
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out stop words and short words (keep words longer than 2 characters)
        terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return terms
    
    def extract_location(self, query: str) -> str:
        """Extract location from query if mentioned"""
        # Common city/country names - aligned with llm_query_parser patterns
        locations = ['riyadh', 'riyad', 'jeddah', 'jiddah', 'dammam', 'damam', 'khobar', 'mecca', 'medina', 
                     'ksa', 'saudi arabia', 'saudi', 'kingdom of saudi arabia',
                     'pakistan', 'pakistani', 'karachi', 'lahore', 'islamabad']
        
        query_lower = query.lower()
        for loc in locations:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(loc) + r'\b'
            if re.search(pattern, query_lower):
                return loc.capitalize()
        
        return None
    
    def extract_gender_from_query(self, query: str) -> Optional[str]:
        """Extract gender from query if mentioned - enhanced with word boundaries and priority matching"""
        # Gender patterns aligned with llm_query_parser.py
        gender_patterns = {
            'female': ['female', 'women', 'woman', 'ladies', 'lady', 'she', 'her', 'females', 'girl', 'girls'],
            'male': ['male', 'men', 'man', 'gentlemen', 'gentleman', 'he', 'his', 'males', 'boy', 'boys']
        }
        
        query_lower = query.lower()
        
        # Priority: Check for explicit gender terms first (most reliable)
        # Use word boundaries to avoid false matches
        for gender_value, patterns in gender_patterns.items():
            for pattern in patterns:
                # Use word boundary regex for better matching
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower):
                    print(f"✓ PeopleFinder: Gender pattern matched: '{pattern}' -> '{gender_value}' in query: '{query}'")
                    return gender_value
        
        return None

    def extract_role_keywords(self, query: str) -> List[str]:
        """Extract role-related keywords - aligned with llm_query_parser job_titles_patterns"""
        # Enhanced role keywords matching llm_query_parser patterns
        role_keywords = {
            'ceo': ['ceo', 'chief executive', 'chief executive officer'],
            'cto': ['cto', 'chief technology', 'chief tech officer'],
            'cio': ['cio', 'chief information', 'chief information officer'],
            'cdo': ['cdo', 'chief data', 'chief data officer'],
            'director': ['director', 'head of', 'head'],
            'manager': ['manager', 'managing', 'product manager', 'product managers'],
            'lead': ['lead', 'leader', 'leading', 'decision maker', 'decision makers', 'innovation leader', 'innovation leaders'],
            'founder': ['founder', 'co-founder', 'cofounder'],
            'executive': ['executive', 'exec', 'vp', 'vice president'],
            'engineer': ['engineer', 'engineering'],
            'developer': ['developer', 'development'],
            'architect': ['architect', 'architecture'],
            'consultant': ['consultant', 'consulting'],
            'analyst': ['analyst', 'analysis']
        }
        
        query_lower = query.lower()
        found_roles = []
        
        # Use word boundaries for better matching
        for role_key, patterns in role_keywords.items():
            for pattern in patterns:
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower):
                    if role_key not in found_roles:
                        found_roles.append(role_key)
                    break
        
        return found_roles
    
    def extract_industry_keywords(self, query: str) -> List[str]:
        """Extract industry keywords - aligned with llm_query_parser industries_patterns"""
        # Industry patterns matching llm_query_parser patterns
        industries_patterns = {
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning'],
            'analytics': ['analytics', 'data analytics', 'business intelligence', 'bi'],
            'iot': ['iot', 'internet of things', 'smart city', 'smart cities', 'industry 4.0'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'cloud computing'],
            'devops': ['devops', 'dev ops', 'ci/cd', 'continuous integration'],
            'mobile': ['mobile', 'ios', 'android', 'app development'],
            'web': ['web', 'web application', 'web development'],
            'healthcare': ['healthcare', 'health tech', 'healthtech', 'medical', 'digital health'],
            'fintech': ['fintech', 'financial technology', 'banking', 'finance', 'blockchain'],
            'retail': ['retail', 'ecommerce', 'e-commerce', 'ecommerce'],
            'education': ['education', 'edtech', 'e-learning'],
            'energy': ['energy', 'utilities', 'power', 'oil', 'gas'],
            'construction': ['construction', 'infrastructure', 'engineering'],
            'telecom': ['telecom', 'telecommunications', 'mobile operator'],
            'automotive': ['automotive', 'automobile', 'car', 'vehicle'],
            'tourism': ['tourism', 'travel', 'hospitality'],
            'gis': ['gis', 'geographic information system', 'mapping', 'geospatial'],
            'cybersecurity': ['cybersecurity', 'security', 'compliance'],
        }
        
        query_lower = query.lower()
        found_industries = []
        
        # Use word boundaries for better matching
        for industry_key, patterns in industries_patterns.items():
            for pattern in patterns:
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower):
                    if industry_key not in found_industries:
                        found_industries.append(industry_key)
                    break
        
        return found_industries
    
    def search(self, query: str, max_results: int = 10, min_completeness: float = 50.0) -> List[SearchResult]:
        """
        Search for people based on natural language query with gender filtering
        """
        # Extract query components
        query_terms = self.extract_query_terms(query)
        location = self.extract_location(query)
        role_keywords = self.extract_role_keywords(query)
        industry_keywords = self.extract_industry_keywords(query)
        gender = self.extract_gender_from_query(query)
        
        # Debug: Log extracted components
        if gender:
            print(f"✓ PeopleFinder: Gender filter extracted: '{gender}' from query: '{query}'")
        if industry_keywords:
            print(f"✓ PeopleFinder: Industry keywords extracted: {industry_keywords} from query: '{query}'")
        
        # Combine all search terms (industries are important for matching)
        all_terms = query_terms + role_keywords + industry_keywords
        
        if not all_terms:
            # If no terms extracted, use full query
            all_terms = [q.lower() for q in query.split() if len(q) > 2]
        
        # Gender normalization mapping
        gender_normalization = {
            'f': 'female', 'female': 'female', 'females': 'female',
            'm': 'male', 'male': 'male', 'males': 'male'
        }
        
        query_gender_normalized = None
        if gender:
            query_gender_normalized = gender_normalization.get(gender.lower().strip(), gender.lower().strip())
        
        # Score all people
        scored_results = []
        seen_ids = set()
        gender_filtered_count = 0
        no_gender_count = 0
        
        for person in self.people:
            # Skip incomplete profiles
            if person.profile_completeness < min_completeness:
                continue
            
            # Skip duplicates
            if person.id in seen_ids:
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
            
            # Calculate score (pass gender for scoring boost)
            score, breakdown = self.scoring_engine.calculate_total_score(
                person, all_terms, location, seniority_levels=role_keywords, query_gender=query_gender_normalized
            )
            
            # Generate explanation
            explanation = self.scoring_engine.generate_explanation(
                person, breakdown, all_terms, location
            )
            
            scored_results.append(SearchResult(
                person=person,
                relevance_score=round(score, 2),
                score_breakdown=breakdown,
                explanation=explanation
            ))
            
            seen_ids.add(person.id)
        
        # Debug: Log gender filtering stats
        if query_gender_normalized:
            print(f"✓ PeopleFinder: Gender filter '{query_gender_normalized}' - Results: {len(scored_results)}, Filtered: {gender_filtered_count}, No gender data: {no_gender_count}")
        
        # Sort by relevance score (descending)
        scored_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Return top results
        return scored_results[:max_results]






