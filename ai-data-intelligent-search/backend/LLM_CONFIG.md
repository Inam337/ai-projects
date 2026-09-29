# LLM Query Parser Configuration

This document explains how to configure and use the Local LLM Integration for parsing natural language queries.

## Overview

The LLM Query Parser supports parsing complex natural language queries into structured search parameters. It supports multiple backends:

1. **Ollama** - Local LLM via Ollama API
2. **LM Studio** - OpenAI-compatible local LLM
3. **Rule-based** - Fallback parser (always available)

## Configuration

### Environment Variables

Set these environment variables before starting the server:

```bash
# LLM Backend (options: "ollama", "lmstudio", "rule_based")
export LLM_BACKEND=ollama

# LLM API URL
export LLM_URL=http://localhost:11434  # Default Ollama URL
# For LM Studio: http://localhost:1234/v1
```

### Using Ollama

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama (usually runs automatically)
4. Set environment variables:
   ```bash
   export LLM_BACKEND=ollama
   export LLM_URL=http://localhost:11434
   ```

### Using LM Studio

1. Download LM Studio: https://lmstudio.ai
2. Download a model (e.g., Llama 3.2)
3. Start the local server in LM Studio
4. Set environment variables:
   ```bash
   export LLM_BACKEND=lmstudio
   export LLM_URL=http://localhost:1234/v1
   ```

### Rule-based Fallback

If no LLM is configured or available, the system automatically falls back to rule-based parsing. This works without any additional setup.

## API Usage

### Endpoint: `/api/search/llm`

**POST Request:**
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
  "results": [...],
  "total_results": 10
}
```

## Supported Query Types

### Objective 1: Finding Saudi Professionals

**AI & Analytics:**
- "Show me data analytics leaders in Riyadh working at government organizations."
- "Find female heads of AI or Machine Learning in Saudi banks."
- "List Chief Data Officers in KSA working in retail or ecommerce."

**IoT & Smart Cities:**
- "Who are the IoT or smart city directors at NEOM and The Red Sea Global?"
- "Give me executives in facility management companies in Saudi Arabia with IoT in their job title."

**Cloud & DevOps:**
- "Show me heads of cloud or DevOps at telecom operators in Saudi Arabia."
- "Who are the premium members on LinkedIn working as DevOps leaders in Riyadh?"

**Company-Level Precision:**
- "Who are the senior technology decision makers at Saudi Aramco?"
- "List executives with digital transformation in their title at SABIC."

### Objective 2: Company Matching

**When Pakistani Tech Leaders Visit Saudi Arabia:**
- "If DPL's CEO is visiting Riyadh, which Saudi executives should he meet?"
- "When Systems Limited's leadership team visits Saudi Arabia, which enterprises or ministries should they connect with?"

**Company Discovery:**
- "Show me large Pakistani software companies providing cloud and AI services."
- "List startups in Pakistan specializing in IoT or Industry 4.0 solutions."

## Query Parsing Features

The parser extracts:
- **Job Titles**: CEO, CTO, Director, Manager, Head of AI, etc.
- **Industries**: AI, IoT, Cloud, Healthcare, Fintech, etc.
- **Technologies**: IoT, AI/ML, Cloud, DevOps, Mobile Apps, etc.
- **Locations**: Riyadh, Jeddah, KSA, Saudi Arabia, etc.
- **Companies**: Saudi Aramco, NEOM, STC, etc.
- **Company Types**: government, banks, startups, healthcare providers
- **Gender**: male, female (if specified)
- **Seniority**: executive, director, manager, leader
- **Premium Filter**: premium LinkedIn members

## Examples

### Example 1: Complex Query
```
Query: "Find female heads of AI or Machine Learning in Saudi banks."
```

Parsed:
- Gender: female
- Job Titles: head, head of AI, head of Machine Learning
- Industries: AI, Machine Learning
- Company Types: banks
- Locations: Saudi Arabia

### Example 2: Company Match
```
Query: "If DPL's CEO is visiting Riyadh, which Saudi executives should he meet?"
```

Parsed:
- Objective: objective2
- Query Type: company_match
- Pakistani Company: DPL
- Visit Context: visiting Riyadh
- Job Titles: CEO, executives
- Locations: Riyadh

## Performance

- **With LLM**: More accurate parsing, better understanding of context
- **Rule-based**: Fast, always available, good for common patterns
- **Hybrid**: Automatically falls back to rule-based if LLM unavailable

## Troubleshooting

### LLM Not Connecting

1. Check if LLM service is running:
   ```bash
   # For Ollama
   curl http://localhost:11434/api/tags
   
   # For LM Studio
   curl http://localhost:1234/v1/models
   ```

2. Check environment variables:
   ```bash
   echo $LLM_BACKEND
   echo $LLM_URL
   ```

3. The system will automatically fall back to rule-based parsing if LLM is unavailable.

### Parsing Issues

If queries aren't being parsed correctly:
1. Try rephrasing the query
2. Check server logs for parsing errors
3. Use rule-based parsing for simpler queries

## Integration with Frontend

The frontend can call `/api/search/llm` with natural language queries. The parser handles all the complexity of extracting search parameters.

Example frontend code:
```javascript
const response = await fetch('/api/search/llm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Show me data analytics leaders in Riyadh",
    max_results: 10,
    use_llm: true
  })
});
```


