# LLM Query Parser Implementation Summary

## Overview

A comprehensive Local LLM Integration has been implemented to parse complex natural language queries and execute searches for both Objective 1 (finding Saudi professionals) and Objective 2 (company matching scenarios).

## Files Created

1. **`backend/llm_query_parser.py`** - LLM query parser with support for multiple backends
2. **`backend/query_executor.py`** - Query executor that executes parsed queries
3. **`backend/LLM_CONFIG.md`** - Configuration and usage documentation

## Files Modified

1. **`backend/main.py`** - Added LLM parser initialization and new `/api/search/llm` endpoint
2. **`backend/requirements.txt`** - Added documentation for LLM dependencies

## Features Implemented

### 1. Multi-Backend LLM Support

- **Ollama**: Local LLM via Ollama API (default: http://localhost:11434)
- **LM Studio**: OpenAI-compatible local LLM API
- **Rule-based Fallback**: Always available, works without LLM

### 2. Query Parsing Capabilities

The parser extracts structured information from natural language queries:

- **Job Titles**: CEO, CTO, CIO, Director, Manager, Head of AI, etc.
- **Industries**: AI, Analytics, IoT, Cloud, DevOps, Healthcare, Fintech, etc.
- **Technologies**: IoT, AI/ML, Cloud, DevOps, Mobile Apps, Blockchain, etc.
- **Locations**: Riyadh, Jeddah, KSA, Saudi Arabia, Pakistan, etc.
- **Companies**: Saudi Aramco, NEOM, STC, DPL, Systems Limited, etc.
- **Company Types**: government, banks, startups, healthcare providers, telecom, etc.
- **Gender**: male, female (if specified)
- **Seniority Levels**: executive, director, manager, leader
- **Premium Filter**: premium LinkedIn members
- **Visit Context**: For Objective 2 queries

### 3. Objective Detection

Automatically detects:
- **Objective 1**: Finding Saudi professionals based on various criteria
- **Objective 2**: Company matching scenarios (Pakistani companies visiting Saudi Arabia, etc.)

### 4. Query Types

- **people_search**: Standard people search (Objective 1)
- **company_match**: Match Pakistani companies with Saudi professionals (Objective 2A)
- **company_discovery**: Discover Pakistani companies (Objective 2B/C)

### 5. Advanced Filtering

The query executor applies multiple filters:
- Gender filtering
- Location filtering (city, state, country)
- Company name matching
- Company type matching
- Job title fuzzy matching
- Industry/technology matching
- Premium member filtering

### 6. Smart Re-scoring

Results are re-scored based on:
- Exact job title matches
- Exact company matches
- Exact location matches
- Premium member status

## API Endpoint

### POST `/api/search/llm`

**Request:**
```json
{
  "query": "Show me data analytics leaders in Riyadh working at government organizations.",
  "max_results": 10,
  "use_llm": true
}
```

**Response:**
```json
{
  "query": "Show me data analytics leaders in Riyadh working at government organizations.",
  "results": [
    {
      "id": "P00001",
      "firstName": "John",
      "lastName": "Doe",
      "job_title": "Head of Data Analytics",
      "current_company": "Ministry of Finance",
      "location": "Riyadh, Saudi Arabia",
      "relevance_score": 95.5,
      ...
    }
  ],
  "total_results": 10
}
```

## Configuration

### Environment Variables

```bash
# LLM Backend (options: "ollama", "lmstudio", "rule_based")
export LLM_BACKEND=ollama

# LLM API URL
export LLM_URL=http://localhost:11434  # Default Ollama URL
```

### Setup Instructions

1. **Using Ollama** (Recommended):
   ```bash
   # Install Ollama
   # Download from https://ollama.ai
   
   # Pull a model
   ollama pull llama3.2
   
   # Set environment variables
   export LLM_BACKEND=ollama
   export LLM_URL=http://localhost:11434
   ```

2. **Using LM Studio**:
   ```bash
   # Download LM Studio from https://lmstudio.ai
   # Download a model and start local server
   
   # Set environment variables
   export LLM_BACKEND=lmstudio
   export LLM_URL=http://localhost:1234/v1
   ```

3. **Rule-based (No Setup Required)**:
   - Works automatically if LLM is not available
   - No configuration needed

## Supported Query Examples

### Objective 1 Examples

✅ "Show me data analytics leaders in Riyadh working at government organizations."
✅ "Find female heads of AI or Machine Learning in Saudi banks."
✅ "List Chief Data Officers in KSA working in retail or ecommerce."
✅ "Who are the IoT or smart city directors at NEOM and The Red Sea Global?"
✅ "Show me heads of cloud or DevOps at telecom operators in Saudi Arabia."
✅ "Who are the premium members on LinkedIn working as DevOps leaders in Riyadh?"
✅ "Who are the senior technology decision makers at Saudi Aramco?"
✅ "List executives with digital transformation in their title at SABIC."

### Objective 2 Examples

✅ "If DPL's CEO is visiting Riyadh, which Saudi executives should he meet?"
✅ "When Systems Limited's leadership team visits Saudi Arabia, which enterprises or ministries should they connect with?"
✅ "If NETSOL's CEO is in Riyadh, list potential leaders in automotive finance companies."
✅ "Show me large Pakistani software companies providing cloud and AI services."
✅ "List startups in Pakistan specializing in IoT or Industry 4.0 solutions."

## Architecture

```
User Query (Natural Language)
    ↓
LLM Query Parser
    ├─→ LLM Backend (Ollama/LM Studio) [Optional]
    └─→ Rule-based Parser [Fallback]
    ↓
ParsedQuery (Structured)
    ├─→ Objective (1 or 2)
    ├─→ Query Type
    ├─→ Job Titles, Industries, Technologies
    ├─→ Locations, Companies, Company Types
    └─→ Filters (Gender, Premium, etc.)
    ↓
Query Executor
    ├─→ Hybrid Search Engine
    ├─→ Company Matcher
    └─→ Filter Application
    ↓
Search Results (Filtered & Re-scored)
```

## Performance

- **LLM Parsing**: More accurate, better context understanding
- **Rule-based**: Fast, always available, good for common patterns
- **Automatic Fallback**: Seamlessly falls back if LLM unavailable

## Error Handling

- Graceful fallback to rule-based parsing if LLM unavailable
- Comprehensive error messages
- Continues to work even if LLM service is down

## Testing

Test the endpoint with curl:

```bash
curl -X POST http://localhost:8000/api/search/llm \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me data analytics leaders in Riyadh working at government organizations.",
    "max_results": 10,
    "use_llm": true
  }'
```

## Next Steps

1. **Install LLM Backend** (Optional but Recommended):
   - Install Ollama or LM Studio
   - Pull/download a model
   - Set environment variables

2. **Test the Endpoint**:
   - Use the `/api/search/llm` endpoint with sample queries
   - Verify parsing accuracy
   - Check search results quality

3. **Frontend Integration**:
   - Update frontend to use `/api/search/llm` endpoint
   - Handle natural language queries from users
   - Display parsed query information (optional)

## Notes

- The system works without LLM (rule-based fallback)
- LLM improves parsing accuracy for complex queries
- All Objective 1 and Objective 2 queries are supported
- Backward compatible with existing `/api/search/people` endpoint


