# People Finder & Company Matchmaking Backend

A FastAPI backend for finding professionals and matching companies with people.

## Setup

1. Generate dummy datasets (if not already generated):
```bash
cd backend
python generate_dummy_data.py
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

Or:
```bash
python main.py
```

## Features

### 1. Private People Finder Engine
- Natural language search across professional profiles
- Semantic query interpretation
- Relevance scoring with explanations
- Profile completeness filtering

### 2. Company-People Matchmaking Engine
- Match Pakistani IT companies with relevant expat professionals
- Location-based filtering
- Industry and service alignment
- Contextual matching criteria

### 3. Smart Recommendation & Scoring Engine
- Composite relevance score (0-100)
- Configurable scoring weights
- Score breakdown by component
- Transparent explanations

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with API information and data stats
- `GET /health` - Health check endpoint

### People Search
- `POST /api/search/people` - Search for professionals using natural language
  - Body: `{"query": "CIO in Riyadh", "max_results": 10, "min_completeness": 50.0}`
  
- `GET /api/people/{person_id}` - Get person profile by ID

### Company Matchmaking
- `POST /api/match/company` - Match company with professionals
  - Body: `{"company_name": "DPL Technologies", "target_city": "Riyadh", "max_results": 5}`
  
- `GET /api/companies` - List all Pakistani companies
- `GET /api/companies/{company_name}` - Get company information by name

### Query Management
- `POST /api/queries/save` - Save a search query
- `GET /api/queries` - List all saved queries
- `GET /api/queries/{query_id}` - Get saved query by ID
- `PUT /api/queries/{query_id}/rename` - Rename a saved query
- `DELETE /api/queries/{query_id}` - Delete a saved query

### Scoring Configuration
- `GET /api/scoring/weights` - Get current scoring weights
- `PUT /api/scoring/weights` - Update scoring weights
  - Body: `{"industry_alignment": 0.30, "role_relevance": 0.25, "location_proximity": 0.20, "profile_completeness": 0.25}`

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Dataset Structure

### Dataset A - People (dataset_a_people.csv)
Contains professional profiles with fields:
- id, firstName, lastName, gender
- job_title, headline, location
- industry, seniority, current_company
- linkedinUrl, profilePictureUrl
- premium, jobSeeker status

### Dataset B - Pakistani Companies (dataset_b_pakistani_companies.csv)
Contains Pakistani IT company profiles with fields:
- account_name_profile, account_name_clean
- industry, account_services
- account_city, account_country
- technologies, keywords
- employee_count, founded_year

## Scoring Components

The scoring engine uses four weighted components:
1. **Industry Alignment** (default: 30%) - Matches person's industry with query/company
2. **Role Relevance** (default: 25%) - Matches job title and seniority
3. **Location Proximity** (default: 20%) - Matches location requirements
4. **Profile Completeness** (default: 25%) - Quality of profile data

Weights can be adjusted via the `/api/scoring/weights` endpoint.

