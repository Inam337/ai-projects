# API Test Examples - cURL Commands

Base URL: `http://localhost:8000`

## Prerequisites
Make sure the server is running:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

---

## 1. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

---

## 2. Root Endpoint (API Info)
```bash
curl -X GET "http://localhost:8000/"
```

---

## 3. Search People - Basic Query
```bash
curl -X POST "http://localhost:8000/api/search/people" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CIO in Riyadh",
    "max_results": 5,
    "min_completeness": 50.0
  }'
```

---

## 4. Search People - Software Engineer
```bash
curl -X POST "http://localhost:8000/api/search/people" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Senior Software Engineer in IT Services",
    "max_results": 10
  }'
```

---

## 5. Search People - Director Level
```bash
curl -X POST "http://localhost:8000/api/search/people" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Director in Cloud Computing",
    "max_results": 8
  }'
```

---

## 6. Get Person by ID
Replace `P00001` with an actual person ID from search results:
```bash
curl -X GET "http://localhost:8000/api/people/P00001"
```

---

## 7. List All Pakistani Companies
```bash
curl -X GET "http://localhost:8000/api/companies"
```

---

## 8. Get Company by Name
Replace `DPL Technologies` with an actual company name:
```bash
curl -X GET "http://localhost:8000/api/companies/DPL Technologies"
```

---

## 9. Match Company with People - DPL Technologies
```bash
curl -X POST "http://localhost:8000/api/match/company" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "DPL Technologies",
    "target_city": "Riyadh",
    "max_results": 5
  }'
```

---

## 10. Match Company with People - Different Company
```bash
curl -X POST "http://localhost:8000/api/match/company" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechSolutions Pakistan",
    "target_city": "Jeddah",
    "max_results": 3
  }'
```

---

## 11. Save Query
```bash
curl -X POST "http://localhost:8000/api/queries/save" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CTO in Saudi Arabia",
    "name": "CTO Search",
    "query_type": "people_search"
  }'
```

---

## 12. List All Saved Queries
```bash
curl -X GET "http://localhost:8000/api/queries"
```

---

## 13. List Queries by Type
```bash
curl -X GET "http://localhost:8000/api/queries?query_type=people_search"
```

---

## 14. Get Query by ID
Replace `Q0001` with an actual query ID:
```bash
curl -X GET "http://localhost:8000/api/queries/Q0001"
```

---

## 15. Rename Query
Replace `Q0001` with an actual query ID:
```bash
curl -X PUT "http://localhost:8000/api/queries/Q0001/rename" \
  -H "Content-Type: application/json" \
  -d '{
    "new_name": "Updated CTO Search"
  }'
```

---

## 16. Delete Query
Replace `Q0001` with an actual query ID:
```bash
curl -X DELETE "http://localhost:8000/api/queries/Q0001"
```

---

## 17. Get Current Scoring Weights
```bash
curl -X GET "http://localhost:8000/api/scoring/weights"
```

---

## 18. Update Scoring Weights
```bash
curl -X PUT "http://localhost:8000/api/scoring/weights" \
  -H "Content-Type: application/json" \
  -d '{
    "industry_alignment": 0.35,
    "role_relevance": 0.30,
    "location_proximity": 0.20,
    "profile_completeness": 0.15
  }'
```

---

## Example Responses

### Search People Response:
```json
{
  "query": "CIO in Riyadh",
  "results": [
    {
      "id": "P00001",
      "firstName": "Ahmed",
      "lastName": "Al-Saud",
      "full_name": "Ahmed Al-Saud",
      "job_title": "Chief Technology Officer",
      "headline": "Technology leader driving innovation",
      "location": "Riyadh, Saudi Arabia",
      "industry": "IT Services",
      "current_company": "Saudi Telecom Company",
      "seniority": "C-Level",
      "gender": "Male",
      "profilePictureUrl": "https://example.com/profiles/ahmed_al-saud_0.jpg",
      "linkedinUrl": "https://www.linkedin.com/in/ahmed-al-saud-0",
      "profile_completeness": 88.89,
      "relevance_score": 85.5,
      "explanation": "Strong industry alignment (IT Services). Relevant role (Chief Technology Officer). Based in Riyadh, Saudi Arabia."
    }
  ],
  "total_results": 5
}
```

### Company Match Response:
```json
{
  "company_name": "DPL Technologies",
  "matched_professionals": [
    {
      "id": "P00001",
      "firstName": "Ahmed",
      "lastName": "Al-Saud",
      "full_name": "Ahmed Al-Saud",
      "job_title": "Chief Technology Officer",
      "location": "Riyadh, Saudi Arabia",
      "industry": "IT Services",
      "relevance_score": 90.2,
      "explanation": "Expert in IT Services industry. Strong industry alignment (IT Services). Relevant role (Chief Technology Officer)."
    }
  ],
  "matching_criteria": "Industry: IT Services; Services: Enterprise Software Development; Location: Riyadh"
}
```

---

## Testing with Python requests

Save the following as `test_api.py`:
```python
import requests

BASE_URL = "http://localhost:8000"

# Search people
response = requests.post(
    f"{BASE_URL}/api/search/people",
    json={"query": "CIO in Riyadh", "max_results": 5}
)
print(response.json())

# Match company
response = requests.post(
    f"{BASE_URL}/api/match/company",
    json={"company_name": "DPL Technologies", "target_city": "Riyadh"}
)
print(response.json())
```

Run: `python test_api.py`






