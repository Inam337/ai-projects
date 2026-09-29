# Pattern-Based Search & Company Matching Features

## Overview

This document describes the new pattern-based query enhancement and Saudi-Pakistani company matching features.

## 1. Pattern-Based Query Enhancement

### Purpose
Enhances natural language queries with regex pattern matching to improve vector search accuracy, especially for queries like "list of all developer in ksa".

### Implementation
- **File**: `backend/pattern_query_enhancer.py`
- **Class**: `PatternQueryEnhancer`

### Features
- Extracts job titles using pattern matching (developer, engineer, manager, director, etc.)
- Extracts locations (KSA, Riyadh, Jeddah, etc.)
- Identifies quantity modifiers (all, top, some, many)
- Filters out natural language query patterns
- Builds enhanced queries for better vector search matching

### Usage
The pattern enhancer is automatically integrated into `VectorSearchEngine`:
- Queries are automatically enhanced before vector encoding
- Pattern information is logged for debugging
- Enhanced queries improve semantic matching accuracy

### Example
**Input Query**: "list of all developer in ksa"
**Enhanced Query**: "developer ksa"
**Extracted Patterns**:
- Job Titles: ['developer']
- Locations: ['ksa']
- Quantity Modifier: 'all'

## 2. Saudi-Pakistani Company Matching

### Purpose
Matches Pakistani companies with best-fit Saudi companies for business partnerships, showing top 5 results with compatibility scores.

### Implementation
- **File**: `backend/saudi_pakistani_company_matcher.py`
- **Class**: `SaudiPakistaniCompanyMatcher`

### Features
- Industry-based matching (40% weight)
- Technology overlap scoring (30% weight)
- Keyword overlap scoring (20% weight)
- Service compatibility (10% weight)
- Company size complementarity
- Detailed match reasons

### API Endpoint

**POST** `/api/match/saudi-pakistani`

**Request Body**:
```json
{
  "pakistani_company_name": "Systems Limited",
  "top_n": 5
}
```

**Response**:
```json
{
  "pakistani_company": "Systems Limited",
  "total_matches": 5,
  "matches": [
    {
      "pakistani_company": {
        "name": "Systems Limited",
        "industry": "Information Technology",
        "location": "Karachi"
      },
      "saudi_company": {
        "name": "Saudi Aramco",
        "industry": "Energy",
        "location": "Dhahran",
        "employee_count": 70000,
        "website": "https://www.aramco.com",
        "linkedin_url": "https://linkedin.com/company/saudi-aramco"
      },
      "match_score": 85.5,
      "compatibility_score": 78.2,
      "match_reasons": [
        "Shared technologies: cloud, ai, data analytics",
        "Common focus areas: digital transformation, innovation"
      ]
    }
  ]
}
```

### Matching Algorithm

1. **Industry Match** (40%): Exact or related industry matching
2. **Technology Overlap** (30%): Common technologies between companies
3. **Keyword Overlap** (20%): Shared keywords and focus areas
4. **Service Compatibility** (10%): Complementary services

### Compatibility Factors

- **Size Complementarity**: Companies with complementary sizes score higher
- **Technology Complementarity**: 30-70% technology overlap is optimal
- **Service Complementarity**: Different but related services are preferred
- **Description Similarity**: Similar business descriptions boost compatibility

## 3. Integration Points

### Vector Search Integration
- Pattern enhancement is automatically applied in `VectorSearchEngine.semantic_search()`
- Enhanced queries improve semantic matching
- Pattern information is logged for debugging

### Hybrid Search Integration
- Hybrid search automatically benefits from pattern enhancement through vector search
- BM25 lexical search + pattern-enhanced semantic re-ranking

### API Integration
- New endpoint: `/api/match/saudi-pakistani`
- Automatically initialized on startup if both Pakistani and Saudi companies are loaded
- Returns top N matches (default: 5) with detailed compatibility information

## 4. Usage Examples

### Pattern-Enhanced Search
```python
# Query: "list of all developer in ksa"
# Automatically enhanced to: "developer ksa"
# Better matches developers in KSA
```

### Company Matching
```bash
curl -X POST "http://localhost:8000/api/match/saudi-pakistani" \
  -H "Content-Type: application/json" \
  -d '{
    "pakistani_company_name": "Systems Limited",
    "top_n": 5
  }'
```

## 5. Dependencies

- `re` (built-in): For regex pattern matching
- `rapidfuzz`: For fuzzy string matching in company matcher
- `sentence-transformers`: For vector embeddings (already required)

## 6. Configuration

No additional configuration needed. Features are automatically enabled when:
- Pattern enhancer: Always available (no dependencies)
- Company matcher: Enabled when both Pakistani and Saudi companies are loaded

## 7. Performance

- Pattern enhancement: Minimal overhead (< 1ms per query)
- Company matching: O(n*m) where n = Pakistani companies, m = Saudi companies
- Results are cached in memory for repeated queries

