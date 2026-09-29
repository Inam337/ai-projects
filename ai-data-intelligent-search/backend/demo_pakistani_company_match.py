"""
Demonstration: Pakistani Company Matching with People
Shows how queries like "DPL meet best person in saudi arabia country" are processed
"""

import json
from llm_query_parser import LLMQueryParser, ParsedQuery

def demonstrate_query_parsing():
    """Demonstrate query parsing for Pakistani company matching"""
    
    # Initialize parser
    parser = LLMQueryParser(
        llm_backend="rule_based",  # Using rule-based for demonstration
        data_dir="datasets"
    )
    
    # Example query
    query = "DPL meet best person in saudi arabia country"
    
    print("=" * 80)
    print("PAKISTANI COMPANY MATCHING DEMONSTRATION")
    print("=" * 80)
    print(f"\n[QUERY] Original Query: '{query}'")
    print("\n" + "-" * 80)
    
    # Parse the query
    print("\n[STEP 1] Query Parsing")
    print("-" * 80)
    parsed_query = parser.parse(query, track_stats=False)
    
    # Show parsed results
    print("\n[OK] Parsed Query Structure:")
    print(json.dumps(parsed_query.dict(), indent=2, ensure_ascii=False))
    
    # Show the LLM prompt that would be generated
    print("\n" + "-" * 80)
    print("\n[STEP 2] LLM Prompt (if using LLM backend)")
    print("-" * 80)
    
    # Build the prompt manually to show what would be sent
    objective = parser._detect_objective(query.lower())
    prompt = parser._build_llm_prompt(query, objective)
    
    print("\n" + prompt)
    
    # Show matching logic
    print("\n" + "-" * 80)
    print("\n[STEP 3] Matching Logic Explanation")
    print("-" * 80)
    
    print(f"""
Based on the parsed query, here's how the system would match DPL with people from dataset_a_people:

1. **Company Detection**: 
   - Detected Pakistani company: "{parsed_query.pakistani_company or 'Not detected'}"
   - Query Type: {parsed_query.query_type}
   - Objective: {parsed_query.objective}

2. **Location Filtering**:
   - Target Location: {parsed_query.locations}
   - Visit Context: {parsed_query.visit_context}
   - The system will search for people in: Saudi Arabia (all cities)

3. **Company Attributes Extraction**:
   - The system will load DPL's profile from dataset_b_pakistani_companies.csv
   - Extract: Industry, Services, Technologies, Keywords, Description
   - Use these attributes to find matching professionals

4. **People Matching Process**:
   - Search through dataset_a_people.csv
   - Score each person based on:
     * Industry alignment with DPL's services
     * Technology overlap
     * Location match (Saudi Arabia)
     * Job title relevance (if specified)
     * Keyword matching
   
5. **Scoring**:
   - Each person gets a relevance score (0-100)
   - Higher scores = better match
   - Results sorted by relevance (descending)

6. **Result Format**:
   - Top 5-10 most relevant professionals
   - Each result includes:
     * Person profile (name, title, company, location)
     * Relevance score
     * Explanation of why they match
     * Score breakdown
""")
    
    # Show example result structure
    print("\n" + "-" * 80)
    print("\n[STEP 4] Example Result Structure")
    print("-" * 80)
    
    example_result = {
        "person": {
            "id": "person_12345",
            "name": "Ahmed Al-Saud",
            "title": "Chief Technology Officer",
            "company": "Saudi Tech Corp",
            "location": "Riyadh, Saudi Arabia",
            "industry": "Technology Services",
            "technologies": ["Cloud Computing", "AI/ML", "Digital Transformation"]
        },
        "relevance_score": 87.5,
        "explanation": "Expert in Technology Services industry. Strong match with DPL's cloud and AI services. Located in Riyadh, Saudi Arabia.",
        "score_breakdown": {
            "industry_match": 40.0,
            "technology_overlap": 30.0,
            "location_match": 10.0,
            "keyword_match": 7.5
        }
    }
    
    print("\n" + json.dumps(example_result, indent=2, ensure_ascii=False))
    
    # Show search query
    print("\n" + "-" * 80)
    print("\n[STEP 5] Generated Search Query")
    print("-" * 80)
    print(f"\nSearch Query: '{parsed_query.search_query}'")
    print("\nThis query is used for hybrid search (vector + keyword matching)")
    
    # Show recommendations
    print("\n" + "=" * 80)
    print("\n[RECOMMENDATIONS] Best Practices for Matching")
    print("=" * 80)
    print("""
To get the best matching results for Pakistani companies meeting with Saudi professionals:

1. **Be Specific About Company Name**:
   - Use exact company name: "DPL" or "Systems Limited"
   - The system will match against dataset_b_pakistani_companies.csv

2. **Specify Location Clearly**:
   - "Saudi Arabia" or "KSA" → searches all Saudi cities
   - "Riyadh" → searches only Riyadh
   - "Jeddah" → searches only Jeddah

3. **Add Industry/Technology Context**:
   - "DPL (cloud services) meet executives in Saudi Arabia"
   - "Systems Limited (AI/ML) find CTOs in Riyadh"
   - This helps the matching algorithm prioritize relevant professionals

4. **Specify Job Titles** (optional):
   - "DPL meet CEOs in Saudi Arabia"
   - "DPL meet CTOs and CIOs in Riyadh"
   - Filters to specific roles

5. **Query Patterns That Work Best**:
   [OK] "DPL's CEO is visiting Riyadh, which executives should he meet?"
   [OK] "When Systems Limited visits Saudi Arabia, who should they connect with?"
   [OK] "DPL meet best person in saudi arabia country"
   [OK] "Find relevant professionals for DPL visiting KSA"
   [OK] "Show me executives DPL should meet in Riyadh for cloud partnerships"
""")
    
    print("\n" + "=" * 80)
    print("END OF DEMONSTRATION")
    print("=" * 80)


if __name__ == "__main__":
    demonstrate_query_parsing()

