"""
Local LLM Query Parser
Parses natural language queries into structured search parameters
Supports multiple LLM backends: Ollama, LM Studio, OpenAI-compatible APIs
"""

import json
import re
import os
import csv
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import requests

# Lazy import of query vector store
try:
    from query_vector_store import QueryVectorStore
    QUERY_STORE_AVAILABLE = True
except ImportError:
    QUERY_STORE_AVAILABLE = False
    QueryVectorStore = None


class ParsedQuery(BaseModel):
    """Structured representation of a parsed query"""
    objective: str  # "objective1" or "objective2"
    query_type: str  # "people_search", "company_match", "company_discovery"
    
    # Search parameters
    job_titles: List[str] = []
    industries: List[str] = []
    technologies: List[str] = []
    locations: List[str] = []
    companies: List[str] = []
    company_types: List[str] = []  # "government", "banks", "startups", "healthcare", etc.
    gender: Optional[str] = None  # "male", "female"
    seniority_levels: List[str] = []  # "executive", "director", "manager", etc.
    
    # Objective 2 specific
    pakistani_company: Optional[str] = None  # For Objective 2A
    visit_context: Optional[str] = None  # "visiting riyadh", "attending leap", etc.
    target_sector: Optional[str] = None  # For company discovery
    
    # Additional filters
    premium_only: bool = False
    keywords: List[str] = []
    
    # Revenue and funding filters
    revenue_range: Optional[str] = None  # e.g., "$10–50M", "$10-50M", "10-50 million"
    has_funding: Optional[bool] = None  # True if "recently raised funding" or similar
    recently_raised_funding: bool = False  # True if explicitly mentioned
    
    # Original query
    original_query: str = ""
    
    # Generated search query for hybrid search
    search_query: str = ""


class LLMQueryParser:
    """Parse natural language queries using local LLM or rule-based fallback"""
    
    def __init__(self, llm_backend: str = "ollama", llm_url: str = "http://localhost:11434", 
                 data_dir: str = None, enable_query_store: bool = True):
        """
        Initialize LLM Query Parser
        
        Args:
            llm_backend: "ollama", "lmstudio", "openai", or "rule_based"
            llm_url: Base URL for LLM API
            data_dir: Directory containing datasets (for loading Pakistani companies)
            enable_query_store: Enable vector database for query optimization
        """
        self.llm_backend = llm_backend
        self.llm_url = llm_url
        self.llm_available = False
        
        # Test LLM availability
        if llm_backend != "rule_based":
            self.llm_available = self._test_llm_connection()
        
        # Knowledge base for rule-based parsing
        self._init_knowledge_base(data_dir)
        
        # Initialize query vector store for optimization
        self.query_store = None
        if enable_query_store and QUERY_STORE_AVAILABLE and QueryVectorStore:
            try:
                store_dir = os.path.join(data_dir or os.path.dirname(os.path.abspath(__file__)), "query_store")
                self.query_store = QueryVectorStore(store_dir=store_dir)
                print("[OK] Query vector store: Initialized")
            except Exception as e:
                print(f"Warning: Could not initialize query vector store: {e}")
                self.query_store = None
    
    def _init_knowledge_base(self, data_dir: str = None):
        """Initialize knowledge base for rule-based parsing"""
        self.job_titles_patterns = {
            'ceo': ['ceo', 'chief executive', 'chief executive officer'],
            'cto': ['cto', 'chief technology', 'chief tech officer'],
            'cio': ['cio', 'chief information', 'chief information officer'],
            'cdo': ['cdo', 'chief data', 'chief data officer'],
            'director': ['director', 'head of', 'head'],
            'manager': ['manager', 'managing', 'product manager', 'product managers'],
            'lead': ['lead', 'leader', 'leading', 'decision maker', 'decision makers', 'innovation leader', 'innovation leaders'],
            'founder': ['founder', 'co-founder', 'cofounder'],
            'executive': ['executive', 'exec', 'vp', 'vice president'],
        }
        
        self.industries_patterns = {
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
        
        self.locations_patterns = {
            'ksa': ['ksa', 'saudi arabia', 'saudi', 'kingdom of saudi arabia'],  # KSA first for priority
            'riyadh': ['riyadh', 'riyad'],
            'jeddah': ['jeddah', 'jiddah'],
            'dammam': ['dammam', 'damam'],
            'pakistan': ['pakistan', 'pakistani'],
            'karachi': ['karachi'],
            'lahore': ['lahore'],
            'islamabad': ['islamabad'],
        }
        
        self.company_types_patterns = {
            'government': ['government', 'ministry', 'public sector', 'public-sector', 'government organizations', 'government organization'],
            'banks': ['bank', 'banks', 'banking', 'financial institution'],
            'startups': ['startup', 'startups', 'start-up', 'start-ups'],
            'healthcare': ['hospital', 'hospitals', 'healthcare provider', 'medical center', 'healthcare providers'],
            'telecom': ['telecom', 'telecommunications', 'mobile operator', 'telecom operators', 'telecom operator'],
            'energy': ['energy', 'oil', 'gas', 'petroleum', 'utilities', 'utility'],
            'construction': ['construction', 'infrastructure', 'construction giants'],
            'retail': ['retail', 'retailer', 'fmcg'],
            'tech': ['tech', 'technology', 'software', 'it'],
            'enterprises': ['enterprise', 'enterprises', 'large company', 'corporation'],
            'facility_management': ['facility management', 'facility management companies', 'facility management company'],
            'logistics': ['logistics', 'logistics startups', 'logistics companies'],
        }
        
        self.known_companies = {
            'saudi': [
                'saudi aramco', 'aramco', 'sabic', 'neom', 'red sea global', 'the red sea global',
                'stc', 'stc pay', 'mobily', 'zain', 'snb alahli', 'riyad bank',
                'almarai', 'king faisal specialist hospital', 'dr. sulaiman al habib',
                'al ayuni', 'nesma', 'panda retail', 'savola', 'saudi airlines'
            ],
            'pakistani': []
        }
        
        # Load Pakistani companies from CSV
        self._load_pakistani_companies(data_dir)
    
    def _load_pakistani_companies(self, data_dir: str = None):
        """Load Pakistani company names from CSV file"""
        if data_dir is None:
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(backend_dir, "datasets")
        
        csv_path = os.path.join(data_dir, "dataset_b_pakistani_companies.csv")
        
        if not os.path.exists(csv_path):
            print(f"Warning: Pakistani companies CSV not found at {csv_path}")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                pakistani_companies = []
                for row in reader:
                    company_name = row.get('account_name_profile', '').strip()
                    if company_name:
                        company_lower = company_name.lower()
                        pakistani_companies.append(company_lower)
                        
                        # Also add variations
                        if ' ' in company_name:
                            # Add without "Limited", "Technologies", etc.
                            variations = [
                                company_name.replace(' Limited', '').lower(),
                                company_name.replace(' Technologies', '').lower(),
                                company_name.replace(' Pakistan', '').lower(),
                            ]
                            pakistani_companies.extend(variations)
                        
                        # Add version without spaces (e.g., "10Pearls" -> "10pearls")
                        if ' ' in company_lower:
                            no_spaces = company_lower.replace(' ', '')
                            if no_spaces not in pakistani_companies:
                                pakistani_companies.append(no_spaces)
                        
                        # Add version with numbers preserved (e.g., "10pearls")
                        # Extract alphanumeric version
                        alphanumeric = re.sub(r'[^a-z0-9]', '', company_lower)
                        if alphanumeric and alphanumeric not in pakistani_companies and len(alphanumeric) >= 3:
                            pakistani_companies.append(alphanumeric)
                
                self.known_companies['pakistani'] = list(set(pakistani_companies))
                print(f"Loaded {len(self.known_companies['pakistani'])} Pakistani company names")
        except Exception as e:
            print(f"Error loading Pakistani companies: {e}")
    
    def _test_llm_connection(self) -> bool:
        """Test if LLM backend is available"""
        try:
            if self.llm_backend == "ollama":
                response = requests.get(f"{self.llm_url}/api/tags", timeout=2)
                return response.status_code == 200
            elif self.llm_backend == "lmstudio":
                # LM Studio uses OpenAI-compatible API
                response = requests.get(f"{self.llm_url}/v1/models", timeout=2)
                return response.status_code == 200
            return False
        except:
            return False
    
    def parse(self, query: str, track_stats: bool = True) -> ParsedQuery:
        """
        Parse natural language query into structured parameters
        
        Args:
            query: Natural language query string
            track_stats: Whether to track query statistics
            
        Returns:
            ParsedQuery object with extracted parameters
        """
        query_lower = query.lower()
        
        # Check for similar queries in vector store for optimization
        similar_query_parsed = None
        if self.query_store:
            # Try to find similar queries first
            temp_parsed = self._parse_rule_based(query, self._detect_objective(query_lower))
            similar_queries = self.query_store.find_similar_queries(
                query, temp_parsed.dict(), top_k=1
            )
            if similar_queries and similar_queries[0][1] > 0.85:  # Very high similarity
                similar_query = similar_queries[0][0]
                stats = self.query_store.get_query_stats(similar_query)
                if stats:
                    # Use parsed query from similar query as starting point
                    similar_query_parsed = stats.parsed_query
        
        # Determine objective
        objective = self._detect_objective(query_lower)
        
        # Try LLM parsing first if available
        parsed_query = None
        if self.llm_available and self.llm_backend != "rule_based":
            try:
                parsed_query = self._parse_with_llm(query, objective)
            except Exception as e:
                print(f"LLM parsing failed, using rule-based: {e}")
        
        # Fallback to rule-based parsing
        if not parsed_query:
            parsed_query = self._parse_rule_based(query, objective)
        else:
            # If LLM parsing succeeded but didn't extract gender, try rule-based gender extraction as fallback
            if not parsed_query.gender:
                query_lower = query.lower()
                gender_patterns = {
                    'female': ['female', 'women', 'woman', 'ladies', 'lady', 'she', 'her', 'females', 'girl', 'girls'],
                    'male': ['male', 'men', 'man', 'gentlemen', 'gentleman', 'he', 'his', 'males', 'boy', 'boys']
                }
                
                for gender_value, patterns in gender_patterns.items():
                    for pattern in patterns:
                        pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                        if re.search(pattern_regex, query_lower):
                            parsed_query.gender = gender_value
                            print(f"[OK] Gender extracted via fallback: {gender_value}")
                            break
                    if parsed_query.gender:
                        break
        
        # Optimize search query using vector store
        if self.query_store:
            parsed_dict = parsed_query.dict()
            optimized_search_query = self.query_store.optimize_search_query(query, parsed_dict)
            parsed_query.search_query = optimized_search_query
        
        return parsed_query
    
    def record_query_result(self, query: str, parsed_query: ParsedQuery, 
                           result_count: int, avg_relevance: float):
        """
        Record query result statistics for optimization
        
        Args:
            query: Original query string
            parsed_query: Parsed query object
            result_count: Number of results returned
            avg_relevance: Average relevance score
        """
        if self.query_store:
            self.query_store.add_query(
                query, 
                parsed_query.dict(),
                result_count=result_count,
                avg_relevance=avg_relevance
            )
    
    def get_query_statistics(self) -> Optional[Dict]:
        """Get query statistics summary"""
        if self.query_store:
            return self.query_store.get_statistics_summary()
        return None
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """Get most popular queries"""
        if self.query_store:
            return self.query_store.get_popular_queries(limit)
        return []
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get most recent queries"""
        if self.query_store:
            return self.query_store.get_recent_queries(limit)
        return []
    
    def _detect_objective(self, query_lower: str) -> str:
        """Detect which objective the query belongs to"""
        # Objective 2 indicators - more comprehensive
        obj2_keywords = [
            'pakistani', 'pakistan', 'visiting', 'visit', 'meet', 'connect',
            'partnership', 'collaboration', 'should he meet', 'should they',
            'which companies', 'which executives', 'list potential', 'find relevant',
            'should they connect', 'could be ideal', 'should they approach',
            'attending leap', 'expands into', 'visits ksa', 'visits saudi',
            'show me', 'list', 'find', 'who are', 'show companies', 'when'
        ]
        
        # Check for Pakistani company names (improved matching)
        for company in self.known_companies['pakistani']:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(company) + r'\b'
            if re.search(pattern, query_lower, re.IGNORECASE):
                return "objective2"
            # Also check without word boundaries for partial matches (e.g., "10pearls" in "10pearls visits")
            if company in query_lower:
                return "objective2"
        
        # Check for "CompanyName visits" or "When CompanyName visits" patterns
        visit_patterns = [
            r'when\s+([a-z0-9]+(?:\s+[a-z0-9]+)*)\s+visits?',
            r'([a-z0-9]+(?:\s+[a-z0-9]+)*)\s+visits?\s+(?:ksa|saudi|riyadh|jeddah)',
            r'([a-z0-9]+(?:\s+[a-z0-9]+)*)\s+visiting',
        ]
        for pattern in visit_patterns:
            matches = re.finditer(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    company_candidate = match.group(1).strip()
                    # Check if it matches any Pakistani company
                    for company in self.known_companies['pakistani']:
                        # Direct match
                        if company == company_candidate.lower():
                            return "objective2"
                        # Partial match (e.g., "10pearls" matches "10pearls")
                        if company in company_candidate.lower() or company_candidate.lower() in company:
                            # Check if it's a significant match (at least 3 characters)
                            if len(company_candidate) >= 3:
                                return "objective2"
        
        # Check for possessive forms (e.g., "DPL's CEO", "Systems Limited's leadership")
        possessive_patterns = [
            r"(\w+(?:\s+\w+)*)'s\s+(?:ceo|cto|cio|leadership|team|executives?)",
            r"(?:ceo|cto|cio|leadership|team)\s+of\s+(\w+(?:\s+\w+)*)",
        ]
        for pattern in possessive_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                match_lower = match.lower()
                # Check if it matches any Pakistani company
                for company in self.known_companies['pakistani']:
                    if company in match_lower or match_lower in company:
                        return "objective2"
        
        # Check for Saudi executives visiting Pakistan (reverse Objective 2)
        saudi_exec_patterns = [
            r"ceo\s+of\s+(?:aramco|stc|neom|sabic)",
            r"(?:aramco|stc|neom|sabic)'s\s+(?:ceo|cto|executives?)",
        ]
        for pattern in saudi_exec_patterns:
            if re.search(pattern, query_lower) and ('pakistan' in query_lower or 'visiting' in query_lower):
                return "objective2"
        
        if any(keyword in query_lower for keyword in obj2_keywords):
            return "objective2"
        
        return "objective1"
    
    def _parse_with_llm(self, query: str, objective: str) -> Optional[ParsedQuery]:
        """Parse query using local LLM"""
        prompt = self._build_llm_prompt(query, objective)
        
        if self.llm_backend == "ollama":
            return self._parse_with_ollama(prompt)
        elif self.llm_backend == "lmstudio":
            return self._parse_with_lmstudio(prompt)
        elif self.llm_backend == "openai":
            return self._parse_with_openai(prompt)
        
        return None
    
    def _build_llm_prompt(self, query: str, objective: str) -> str:
        """Build prompt for LLM with enhanced examples"""
        
        # Build list of known Pakistani companies for context
        pakistani_companies_list = ", ".join(self.known_companies['pakistani'][:20])  # First 20 for context
        
        examples = ""
        if objective == "objective2":
            examples = """
EXAMPLES:

Query: "If DPL's CEO is visiting Riyadh, which Saudi executives should he meet?"
{
    "objective": "objective2",
    "query_type": "company_match",
    "pakistani_company": "dpl",
    "visit_context": "visiting riyadh",
    "job_titles": ["ceo", "executive"],
    "locations": ["riyadh"],
    "search_query": "executive ceo riyadh saudi"
}

Query: "When Systems Limited's leadership team visits Saudi Arabia, which enterprises or ministries should they connect with for digital transformation collaborations?"
{
    "objective": "objective2",
    "query_type": "company_match",
    "pakistani_company": "systems limited",
    "visit_context": "visiting saudi arabia",
    "company_types": ["government", "enterprises"],
    "technologies": ["digital transformation"],
    "keywords": ["collaboration", "partnership"],
    "search_query": "digital transformation government enterprises ministry collaboration"
}

Query: "Show me large Pakistani software companies providing cloud and AI services."
{
    "objective": "objective2",
    "query_type": "company_discovery",
    "technologies": ["cloud", "ai"],
    "company_types": ["tech"],
    "keywords": ["large", "software"],
    "search_query": "cloud ai software large"
}

Query: "CEO of Aramco is visiting — which Pakistani companies offer industrial IoT or asset management solutions?"
{
    "objective": "objective2",
    "query_type": "company_discovery",
    "companies": ["aramco"],
    "technologies": ["iot", "industrial iot", "asset management"],
    "keywords": ["solutions"],
    "search_query": "iot industrial asset management solutions"
}

Query: "Find female heads of AI or Machine Learning in Saudi banks."
{
    "objective": "objective1",
    "query_type": "people_search",
    "gender": "female",
    "job_titles": ["head"],
    "industries": ["ai", "machine learning"],
    "company_types": ["banks"],
    "locations": ["saudi"],
    "seniority_levels": ["director"],
    "search_query": "head ai machine learning banks saudi female"
}
"""
        
        return f"""Parse the following natural language query into structured JSON format.

Query: "{query}"

Objective: {objective}

Known Pakistani Companies (for reference): {pakistani_companies_list}...

{examples}

Extract the following information:
- job_titles: List of job titles/roles mentioned (e.g., CEO, CTO, Director, Manager, Head of AI, CIO)
- industries: List of industries/domains (e.g., AI, IoT, Cloud, Healthcare, Fintech, Automotive, Tourism, Edtech)
- technologies: List of technologies mentioned (e.g., IoT, AI/ML, Cloud, DevOps, Mobile Apps, GIS, Blockchain, Cybersecurity)
- locations: List of locations (e.g., Riyadh, Jeddah, KSA, Saudi Arabia, Pakistan, Karachi, Lahore, Islamabad)
- companies: List of specific company names mentioned (Saudi or Pakistani)
- company_types: List of company types (e.g., government, banks, startups, healthcare providers, enterprises, ministries)
- gender: "male" or "female" if explicitly mentioned (e.g., "female", "women", "woman", "male", "men", "man"), null otherwise. IMPORTANT: Only extract if gender is explicitly stated in the query.
- seniority_levels: List of seniority levels (e.g., executive, director, manager, leader)
- pakistani_company: Pakistani company name if mentioned (extract from possessive forms like "DPL's CEO" or "Systems Limited's leadership")
- visit_context: Context about visit/meeting if mentioned (e.g., "visiting riyadh", "attending leap conference", "visiting saudi arabia")
- target_sector: Target sector for company discovery (e.g., "automotive finance", "edtech", "tourism tech", "healthtech", "fintech")
- premium_only: true if "premium" or "premium members" mentioned, false otherwise
- keywords: Additional important keywords from the query (e.g., "partnership", "collaboration", "solutions", "services")

Query Type Rules:
- "company_match": When a Pakistani company is mentioned and asking who to meet/connect with (usually finding Saudi executives)
- "company_discovery": When asking to find/list Pakistani companies based on criteria
- "people_search": Default for finding people/professionals

Return ONLY valid JSON in this format:
{{
    "objective": "{objective}",
    "query_type": "people_search" or "company_match" or "company_discovery",
    "job_titles": [],
    "industries": [],
    "technologies": [],
    "locations": [],
    "companies": [],
    "company_types": [],
    "gender": null,
    "seniority_levels": [],
    "pakistani_company": null,
    "visit_context": null,
    "target_sector": null,
    "premium_only": false,
    "keywords": [],
    "search_query": "optimized search query string combining all extracted terms"
}}"""
    
    def _parse_with_ollama(self, prompt: str) -> Optional[ParsedQuery]:
        """Parse using Ollama API"""
        try:
            response = requests.post(
                f"{self.llm_url}/api/generate",
                json={
                    "model": "llama3.2",  # Default model, can be configured
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                json_str = result.get("response", "")
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    parsed_data["original_query"] = prompt.split('Query: "')[1].split('"')[0] if 'Query: "' in prompt else ""
                    return ParsedQuery(**parsed_data)
        except Exception as e:
            print(f"Ollama parsing error: {e}")
        
        return None
    
    def _parse_with_lmstudio(self, prompt: str) -> Optional[ParsedQuery]:
        """Parse using LM Studio (OpenAI-compatible API)"""
        try:
            response = requests.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "local-model",  # LM Studio uses this
                    "messages": [
                        {"role": "system", "content": "You are a query parser that extracts structured information from natural language queries. Always return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                parsed_data = json.loads(content)
                parsed_data["original_query"] = prompt.split('Query: "')[1].split('"')[0] if 'Query: "' in prompt else ""
                return ParsedQuery(**parsed_data)
        except Exception as e:
            print(f"LM Studio parsing error: {e}")
        
        return None
    
    def _parse_with_openai(self, prompt: str) -> Optional[ParsedQuery]:
        """Parse using OpenAI-compatible API"""
        # Similar to LM Studio
        return self._parse_with_lmstudio(prompt)
    
    def _parse_rule_based(self, query: str, objective: str) -> ParsedQuery:
        """Rule-based parsing fallback"""
        query_lower = query.lower()
        
        # Extract job titles (enhanced for compound titles like "data analytics leaders")
        job_titles = self._extract_job_titles_enhanced(query_lower)
        
        # Extract industries (with OR support)
        industries = self._extract_patterns_with_or(query_lower, self.industries_patterns)
        
        # Extract technologies (with OR support)
        technologies = self._extract_technologies(query_lower)
        
        # Extract locations (KSA should be prioritized)
        locations = self._extract_patterns(query_lower, self.locations_patterns)
        
        # Ensure KSA is extracted if "ksa" or "saudi" is mentioned
        if 'ksa' in query_lower or ('saudi' in query_lower and 'arabia' in query_lower):
            if 'ksa' not in locations:
                locations.insert(0, 'ksa')  # Add KSA at the beginning for priority
        
        # Extract companies (improved with "The" prefix and "such as" patterns)
        companies = self._extract_companies(query)
        
        # Extract company types (with OR support)
        company_types = self._extract_patterns_with_or(query_lower, self.company_types_patterns)
        
        # Extract gender - enhanced detection with word boundaries and priority
        gender = None
        gender_patterns = {
            'female': ['female', 'women', 'woman', 'ladies', 'lady', 'she', 'her', 'females', 'girl', 'girls'],
            'male': ['male', 'men', 'man', 'gentlemen', 'gentleman', 'he', 'his', 'males', 'boy', 'boys']
        }
        
        # Priority: Check for explicit gender terms first (most reliable)
        # Use word boundaries to avoid false matches
        for gender_value, patterns in gender_patterns.items():
            for pattern in patterns:
                # Use word boundary regex for better matching
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, query_lower):
                    gender = gender_value
                    print(f"[OK] Gender pattern matched: '{pattern}' -> '{gender_value}' in query: '{query}'")
                    break
            if gender:
                break
        
        # Debug: Print extracted gender for verification
        if gender:
            print(f"[OK] Gender extracted: {gender} from query: '{query[:100]}...'")
        else:
            print(f"[INFO] No gender pattern found in query: '{query[:100]}...'")
        
        # Extract seniority
        seniority_levels = []
        if any(word in query_lower for word in ['executive', 'exec', 'vp', 'vice president']):
            seniority_levels.append('executive')
        if any(word in query_lower for word in ['director', 'head of', 'head']):
            seniority_levels.append('director')
        if any(word in query_lower for word in ['manager', 'managing']):
            seniority_levels.append('manager')
        if any(word in query_lower for word in ['leader', 'leading', 'lead']):
            seniority_levels.append('leader')
        
        # Extract Pakistani company (Objective 2) - improved detection
        pakistani_company = None
        
        # Check for "CompanyName visits" or "When CompanyName visits" patterns first
        visit_patterns = [
            r'when\s+([a-z0-9]+(?:\s+[a-z0-9]+)*)\s+visits?',
            r'([a-z0-9]+(?:\s+[a-z0-9]+)*)\s+visits?\s+(?:ksa|saudi|riyadh|jeddah|saudi arabia)',
            r'([a-z0-9]+(?:\s+[a-z0-9]+)*)\s+visiting',
        ]
        for pattern in visit_patterns:
            matches = re.finditer(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    company_candidate = match.group(1).strip().lower()
                    # Check if it matches any Pakistani company
                    for company in self.known_companies['pakistani']:
                        # Direct match
                        if company == company_candidate:
                            pakistani_company = company
                            break
                        # Partial match (e.g., "10pearls" matches "10pearls")
                        if company in company_candidate or company_candidate in company:
                            # Check if it's a significant match (at least 3 characters)
                            if len(company_candidate) >= 3:
                                pakistani_company = company
                                break
                    if pakistani_company:
                        break
            if pakistani_company:
                break
        
        # Check for possessive forms (e.g., "DPL's CEO", "Systems Limited's leadership")
        if not pakistani_company:
            possessive_patterns = [
                r"(\w+(?:\s+\w+)*)'s\s+(?:ceo|cto|cio|leadership|team|executives?|division)",
                r"(?:ceo|cto|cio|leadership|team|executives?)\s+of\s+(\w+(?:\s+\w+)*)",
            ]
            
            for pattern in possessive_patterns:
                matches = re.findall(pattern, query_lower)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    match_lower = match.lower()
                    # Check if it matches any Pakistani company
                    for company in self.known_companies['pakistani']:
                        if company in match_lower or match_lower in company:
                            pakistani_company = company
                            break
                    if pakistani_company:
                        break
                if pakistani_company:
                    break
        
        # Direct company name check (with word boundaries and without)
        if not pakistani_company:
            for company in self.known_companies['pakistani']:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(company) + r'\b'
                if re.search(pattern, query_lower):
                    pakistani_company = company
                    break
                # Also check without word boundaries for partial matches
                if company in query_lower:
                    pakistani_company = company
                    break
        
        # Extract visit context - enhanced (check KSA first)
        visit_context = None
        visit_keywords = ['visiting', 'visit', 'attending', 'expands into', 'visits']
        if any(keyword in query_lower for keyword in visit_keywords):
            # Check for KSA first (most specific)
            if 'ksa' in query_lower or 'saudi arabia' in query_lower or 'saudi' in query_lower:
                visit_context = "visiting saudi arabia"
            elif 'riyadh' in query_lower:
                visit_context = "visiting riyadh"
            elif 'jeddah' in query_lower:
                visit_context = "visiting jeddah"
            elif 'leap' in query_lower or 'conference' in query_lower:
                visit_context = "attending leap conference"
            elif 'pakistan' in query_lower:
                visit_context = "visiting pakistan"
            else:
                # Default to visiting if visit keyword is present but no location specified
                visit_context = "visiting"
        
        # Extract target sector for company discovery
        target_sector = None
        sector_patterns = [
            (r'automotive\s+finance', 'automotive finance'),
            (r'ecommerce\s+or\s+mobility', 'ecommerce mobility'),
            (r'edtech\s+or\s+tourism\s+tech', 'edtech tourism'),
            (r'healthcare|health\s+tech|digital\s+health', 'healthcare'),
            (r'fintech|financial', 'fintech'),
            (r'iot|industry\s+4\.0|industrial', 'iot'),
            (r'gis|smart\s+city|infrastructure', 'gis smart city'),
            (r'cybersecurity|security|compliance', 'cybersecurity'),
        ]
        for pattern, sector in sector_patterns:
            if re.search(pattern, query_lower):
                target_sector = sector
                break
        
        # Premium filter
        premium_only = 'premium' in query_lower or 'premium members' in query_lower
        
        # Extract revenue range (e.g., "$10–50M", "$10-50M", "10-50 million")
        revenue_range = None
        revenue_patterns = [
            r'\$(\d+)[–-](\d+)M',  # $10-50M
            r'\$(\d+)[–-](\d+)\s*million',  # $10-50 million
            r'(\d+)[–-](\d+)\s*million',  # 10-50 million
            r'revenue\s+range\s+of\s+\$?(\d+)[–-](\d+)M?',  # revenue range of $10-50M
        ]
        for pattern in revenue_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                revenue_range = f"${match.group(1)}-{match.group(2)}M"
                break
        
        # Extract funding status
        has_funding = None
        recently_raised_funding = False
        if re.search(r'recently\s+raised\s+funding', query_lower, re.IGNORECASE):
            recently_raised_funding = True
            has_funding = True
        elif re.search(r'raised\s+funding', query_lower, re.IGNORECASE):
            has_funding = True
        elif 'funding' in query_lower and ('raised' in query_lower or 'received' in query_lower):
            has_funding = True
        
        # Extract additional keywords (excluding natural language query patterns)
        keywords = []
        keyword_patterns = [
            'partnership', 'collaboration', 'solutions', 'services', 'digital transformation',
            'asset management', 'training data', 'model development', 'supply chain',
            'public sector', 'government projects', 'funding', 'raised funding', 'recently raised',
            'revenue', 'revenue range', 'revenue of', 'cloud migration', 'platforms', 'platform',
            'experience', 'experienced', 'expertise', 'specializing', 'specialized', 'focusing', 'focused'
        ]
        # Natural language query patterns to exclude from keywords
        query_patterns_to_exclude = [
            'who are', 'who is', 'find', 'show me', 'show', 'list', 'list of', 'give me', 'give us',
            'tell me', 'get', 'working', 'working on', 'working at', 'working in', 'work on', 'work at', 'work in'
        ]
        for kw in keyword_patterns:
            if kw in query_lower:
                # Check if it's not part of a query pattern
                is_query_pattern = False
                for pattern in query_patterns_to_exclude:
                    if pattern in query_lower and kw in pattern:
                        is_query_pattern = True
                        break
                if not is_query_pattern:
                    keywords.append(kw)
        
        # Determine query type - enhanced logic
        query_type = "people_search"
        if objective == "objective2":
            # Company match: Pakistani company visiting Saudi Arabia/KSA (highest priority)
            if pakistani_company and ('visiting' in query_lower or 'visit' in query_lower or 'visits' in query_lower or 
                                     'meet' in query_lower or 'connect' in query_lower or 
                                     'ksa' in query_lower or 'saudi' in query_lower):
                query_type = "company_match"
            # Check for company discovery patterns
            elif any(keyword in query_lower for keyword in ['show me', 'list', 'find', 'who are', 'show companies', 
                                'which companies', 'companies in pakistan', 'pakistani companies']):
                query_type = "company_discovery"
            # Check for Saudi executive visiting Pakistan (reverse match)
            elif any(comp in query_lower for comp in ['aramco', 'stc', 'neom', 'sabic', 'mobily']) and 'pakistan' in query_lower:
                query_type = "company_discovery"
            # Default to company discovery if asking about Pakistani companies
            elif 'pakistani' in query_lower and 'companies' in query_lower:
                query_type = "company_discovery"
            # If Pakistani company is detected but no clear pattern, default to company_match
            elif pakistani_company:
                query_type = "company_match"
        
        # Build search query (include gender for better search context)
        search_query = self._build_search_query(
            job_titles, industries, technologies, locations, companies, 
            company_types, keywords=keywords, gender=gender
        )
        
        return ParsedQuery(
            objective=objective,
            query_type=query_type,
            job_titles=job_titles,
            industries=industries,
            technologies=technologies,
            locations=locations,
            companies=companies,
            company_types=company_types,
            gender=gender,
            seniority_levels=seniority_levels,
            pakistani_company=pakistani_company,
            visit_context=visit_context,
            target_sector=target_sector,
            premium_only=premium_only,
            keywords=keywords,
            revenue_range=revenue_range,
            has_funding=has_funding,
            recently_raised_funding=recently_raised_funding,
            original_query=query,
            search_query=search_query
        )
    
    def _extract_patterns(self, text: str, patterns: Dict[str, List[str]]) -> List[str]:
        """Extract patterns from text, handling OR conditions"""
        found = []
        for key, patterns_list in patterns.items():
            for pattern in patterns_list:
                # Use word boundaries for better matching
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, text, re.IGNORECASE):
                    found.append(key)
                    break
        return found
    
    def _extract_patterns_with_or(self, text: str, patterns: Dict[str, List[str]]) -> List[str]:
        """Extract patterns from text, handling OR conditions (e.g., "retail or ecommerce")"""
        found = []
        
        # First, extract patterns normally
        for key, patterns_list in patterns.items():
            for pattern in patterns_list:
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, text, re.IGNORECASE):
                    if key not in found:
                        found.append(key)
                    break
        
        # Then, look for OR patterns (e.g., "retail or ecommerce", "iot or smart city")
        # Pattern: word1 or word2, word1 or word2 or word3
        or_pattern = r'(\w+(?:\s+\w+)*)\s+or\s+(\w+(?:\s+\w+)*)'
        or_matches = re.finditer(or_pattern, text, re.IGNORECASE)
        
        for match in or_matches:
            term1 = match.group(1).lower().strip()
            term2 = match.group(2).lower().strip()
            
            # Check if these terms match any pattern keys
            for key, patterns_list in patterns.items():
                for pattern in patterns_list:
                    pattern_lower = pattern.lower()
                    # Check if term1 or term2 matches this pattern
                    if term1 == pattern_lower or term2 == pattern_lower:
                        if key not in found:
                            found.append(key)
                    # Also check if pattern is contained in term
                    elif pattern_lower in term1 or pattern_lower in term2:
                        if key not in found:
                            found.append(key)
        
        return found
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology keywords, handling OR conditions"""
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'iot', 'internet of things', 'smart city', 'smart cities',
            'cloud', 'aws', 'azure', 'gcp', 'cloud computing',
            'devops', 'dev ops', 'ci/cd', 'continuous integration',
            'mobile', 'ios', 'android', 'app development',
            'web', 'web application', 'web development',
            'blockchain', 'crypto', 'cryptocurrency',
            'gis', 'geographic information system',
            'digital twin', 'digital twins',
            'data analytics', 'business intelligence', 'bi',
            'tableau', 'power bi', 'data visualization'
        ]
        
        found = []
        text_lower = text.lower()
        
        # First, extract technologies normally
        for tech in tech_keywords:
            pattern_regex = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern_regex, text_lower, re.IGNORECASE):
                if tech not in found:
                    found.append(tech)
        
        # Then, look for OR patterns (e.g., "iot or digital twins", "ai or machine learning")
        or_pattern = r'(\w+(?:\s+\w+)*)\s+or\s+(\w+(?:\s+\w+)*)'
        or_matches = re.finditer(or_pattern, text_lower, re.IGNORECASE)
        
        for match in or_matches:
            term1 = match.group(1).strip()
            term2 = match.group(2).strip()
            
            # Check if these terms match any technology keywords
            for tech in tech_keywords:
                tech_lower = tech.lower()
                if term1 == tech_lower or term2 == tech_lower:
                    if tech not in found:
                        found.append(tech)
                elif tech_lower in term1 or tech_lower in term2:
                    if tech not in found:
                        found.append(tech)
        
        return found
    
    def _extract_job_titles_enhanced(self, text: str) -> List[str]:
        """Extract job titles with support for compound titles like 'data analytics leaders'"""
        found = []
        text_lower = text.lower()
        
        # First, extract standard job titles
        for key, patterns_list in self.job_titles_patterns.items():
            for pattern in patterns_list:
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, text_lower, re.IGNORECASE):
                    if key not in found:
                        found.append(key)
                    break
        
        # Extract compound job titles (e.g., "data analytics leaders", "iot directors")
        # Pattern: [industry/tech] + [job title]
        compound_patterns = [
            r'(\w+(?:\s+\w+)*)\s+(leaders?|directors?|heads?|managers?|executives?|officers?)',
            r'(leaders?|directors?|heads?|managers?|executives?|officers?)\s+(?:of|in)\s+(\w+(?:\s+\w+)*)',
        ]
        
        for pattern in compound_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Extract the industry/tech part and job title part
                if len(match.groups()) >= 2:
                    part1 = match.group(1).strip()
                    part2 = match.group(2).strip() if len(match.groups()) > 1 else ""
                    
                    # Check if part1 contains an industry/technology
                    for industry_key, industry_patterns in self.industries_patterns.items():
                        for industry_pattern in industry_patterns:
                            if industry_pattern in part1:
                                # Add the job title from part2
                                for title_key, title_patterns in self.job_titles_patterns.items():
                                    for title_pattern in title_patterns:
                                        if title_pattern in part2:
                                            if title_key not in found:
                                                found.append(title_key)
                                            break
                                break
                    
                    # Also check if part2 contains a job title and part1 might be industry/tech
                    for title_key, title_patterns in self.job_titles_patterns.items():
                        for title_pattern in title_patterns:
                            if title_pattern in part2:
                                # Check if part1 matches any industry/tech
                                for industry_key, industry_patterns in self.industries_patterns.items():
                                    for industry_pattern in industry_patterns:
                                        if industry_pattern in part1:
                                            if title_key not in found:
                                                found.append(title_key)
                                            break
                                break
        
        return found
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names - improved matching with 'The' prefix and list handling"""
        found = []
        all_companies = self.known_companies['saudi'] + self.known_companies['pakistani']
        text_lower = text.lower()
        
        # Normalize text for matching (remove "the" prefix for better matching)
        text_normalized = re.sub(r'\bthe\s+', '', text_lower, flags=re.IGNORECASE)
        
        for company in all_companies:
            company_lower = company.lower()
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(company_lower) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE) or re.search(pattern, text_normalized, re.IGNORECASE):
                if company not in found:
                    found.append(company)
            
            # Also try matching with "The" prefix
            company_with_the = f"the {company_lower}"
            pattern_with_the = r'\b' + re.escape(company_with_the) + r'\b'
            if re.search(pattern_with_the, text_lower, re.IGNORECASE):
                if company not in found:
                    found.append(company)
            
            # Also try matching without "the" prefix
            company_without_the = re.sub(r'^the\s+', '', company_lower, flags=re.IGNORECASE)
            if company_without_the != company_lower:
                pattern = r'\b' + re.escape(company_without_the) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    if company not in found:
                        found.append(company)
        
        # Extract companies from "such as" or "like" patterns with OR
        # Pattern: "such as Company1 or Company2" or "like Company1, Company2, or Company3"
        list_patterns = [
            r'(?:such as|like)\s+([^.,]+?)(?:\s+or\s+|\s*,\s*)([^.,]+?)(?:\s+or\s+|\s*,\s*)?([^.,]+?)?(?:\s+or\s+)?',
            r'(?:such as|like)\s+([^.,]+?)(?:\s+or\s+|\s*,\s*)([^.,]+?)?',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+or\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "Company1 or Company2"
        ]
        
        for pattern in list_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                for company_name in groups:
                    if company_name and company_name.strip():
                        company_clean = company_name.strip()
                        company_clean_lower = company_clean.lower()
                        # Check if it matches any known company (with or without "The")
                        for known_company in all_companies:
                            known_lower = known_company.lower()
                            # Direct match
                            if company_clean_lower == known_lower:
                                if known_company not in found:
                                    found.append(known_company)
                            # Partial match
                            elif company_clean_lower in known_lower or known_lower in company_clean_lower:
                                # Check if it's a significant match (at least 3 characters)
                                if len(company_clean_lower) >= 3:
                                    if known_company not in found:
                                        found.append(known_company)
                            # Match with "The" prefix
                            elif f"the {company_clean_lower}" == known_lower or company_clean_lower == known_lower.replace("the ", ""):
                                if known_company not in found:
                                    found.append(known_company)
        
        # Also look for common patterns
        company_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Hospital|Bank|Group|Company|Corporation|Limited|Ltd|Technologies|Software)',
            r'\b([A-Z][a-z]+)\s+(?:Aramco|SABIC|NEOM|STC|Mobily|Zain)',
            r'\b(?:Saudi\s+)?Aramco\b',
            r'\bSTC\s+Pay\b',
            r'\bDr\.\s+Sulaiman\s+Al\s+Habib\b',
            r'\bThe\s+Red\s+Sea\s+Global\b',  # Handle "The Red Sea Global"
            r'\bKing\s+Faisal\s+Specialist\s+Hospital\b',  # Handle full hospital name
        ]
        
        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                match_text = match.group(0) if match.groups() == () else match.group(1)
                match_lower = match_text.lower()
                # Check if it matches any known company
                for known_company in all_companies:
                    known_lower = known_company.lower()
                    if match_lower in known_lower or known_lower in match_lower:
                        if known_company not in found:
                            found.append(known_company)
                        break
        
        return found
    
    def _build_search_query(self, job_titles: List[str], industries: List[str],
                           technologies: List[str], locations: List[str],
                           companies: List[str], company_types: List[str],
                           keywords: List[str], gender: Optional[str] = None) -> str:
        """Build optimized search query from extracted parameters with semantic enhancement"""
        parts = []
        
        # Query expansion: Add synonyms and related terms
        expanded_terms = self._expand_terms(job_titles, industries, technologies, keywords)
        
        # Prioritize important terms with weights
        # Job titles are most important
        parts.extend(job_titles)
        parts.extend([f"{jt} executive" for jt in job_titles if jt in ['ceo', 'cto', 'cio']])  # Expand C-level
        
        # Industries and technologies are high priority
        parts.extend(industries)
        parts.extend(technologies)
        parts.extend(expanded_terms)
        
        # Keywords are important context
        parts.extend(keywords)
        
        # Company types add context
        parts.extend(company_types)
        
        # Locations are important for filtering
        parts.extend(locations)
        
        # Companies are specific matches
        parts.extend(companies)
        
        # Gender adds important context (but filtering happens separately)
        if gender:
            parts.append(gender)
        
        # Remove duplicates while preserving order and filter natural language patterns
        seen = set()
        unique_parts = []
        natural_language_patterns = {
            'who', 'are', 'find', 'show', 'me', 'list', 'of', 'give', 'us', 'tell', 'get',
            'working', 'work', 'works', 'worked', 'that', 'this', 'these', 'those',
            'which', 'what', 'where', 'when', 'why', 'how', 'there', 'their', 'they', 'them'
        }
        for part in parts:
            if part:
                part_lower = part.lower()
                # Filter out natural language query patterns
                if part_lower not in natural_language_patterns and part_lower not in seen:
                    seen.add(part_lower)
                    unique_parts.append(part)
        
        # Limit query length for optimal search (keep most important terms)
        max_terms = 15
        if len(unique_parts) > max_terms:
            # Keep first max_terms (most important)
            unique_parts = unique_parts[:max_terms]
        
        return " ".join(unique_parts)
    
    def _expand_terms(self, job_titles: List[str], industries: List[str], 
                     technologies: List[str], keywords: List[str]) -> List[str]:
        """Expand terms with synonyms and related concepts"""
        expanded = []
        
        # Job title expansions
        title_expansions = {
            'ceo': ['chief executive', 'executive leader', 'chief executive officer'],
            'cto': ['chief technology', 'technology leader', 'tech executive'],
            'cio': ['chief information', 'information technology leader', 'it executive'],
            'director': ['head', 'lead', 'senior manager'],
            'manager': ['lead', 'supervisor', 'coordinator'],
        }
        
        for title in job_titles:
            if title in title_expansions:
                expanded.extend(title_expansions[title])
        
        # Industry expansions
        industry_expansions = {
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'ml'],
            'iot': ['internet of things', 'smart devices', 'connected devices'],
            'cloud': ['cloud computing', 'cloud services', 'cloud infrastructure'],
            'fintech': ['financial technology', 'fintech solutions', 'digital finance'],
            'healthcare': ['health tech', 'medical technology', 'digital health'],
        }
        
        for industry in industries:
            if industry in industry_expansions:
                expanded.extend(industry_expansions[industry])
        
        # Technology expansions
        tech_expansions = {
            'ai': ['machine learning', 'deep learning', 'neural networks'],
            'iot': ['smart city', 'industry 4.0', 'industrial iot'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud migration'],
        }
        
        for tech in technologies:
            if tech in tech_expansions:
                expanded.extend(tech_expansions[tech])
        
        return expanded
    
    def _clean_natural_language_patterns(self, query: str) -> str:
        """Remove natural language query patterns from query string"""
        if not query:
            return query
        
        # Natural language patterns to remove
        patterns_to_remove = [
            r'\bwho\s+are\b',
            r'\bwho\s+is\b',
            r'\bfind\s+me\b',
            r'\bfind\b',
            r'\bshow\s+me\b',
            r'\bshow\b',
            r'\blist\s+of\b',
            r'\blist\b',
            r'\bgive\s+me\b',
            r'\bgive\s+us\b',
            r'\bgive\b',
            r'\btell\s+me\b',
            r'\btell\b',
            r'\bget\s+me\b',
            r'\bget\b',
            r'\bworking\s+on\b',
            r'\bworking\s+at\b',
            r'\bworking\s+in\b',
            r'\bworking\b',
            r'\bwork\s+on\b',
            r'\bwork\s+at\b',
            r'\bwork\s+in\b',
        ]
        
        cleaned = query
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned


