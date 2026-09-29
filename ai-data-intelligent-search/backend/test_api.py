"""
API Test Examples for People Finder & Company Matchmaking API

Run the server first:
    uvicorn main:app --reload --port 8000

Then run this script or use the examples below.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Helper to print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


# Test 1: Health Check
def test_health_check():
    """GET /health"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("1. Health Check", response)
    return response


# Test 2: Root Endpoint
def test_root():
    """GET /"""
    response = requests.get(f"{BASE_URL}/")
    print_response("2. Root Endpoint (API Info)", response)
    return response


# Test 3: Search People
def test_search_people():
    """POST /api/search/people"""
    payload = {
        "query": "CIO in Riyadh",
        "max_results": 5,
        "min_completeness": 50.0
    }
    response = requests.post(f"{BASE_URL}/api/search/people", json=payload)
    print_response("3. Search People - 'CIO in Riyadh'", response)
    return response


# Test 4: Search People - Different Query
def test_search_people_different():
    """POST /api/search/people - Software Engineer"""
    payload = {
        "query": "Senior Software Engineer in IT Services",
        "max_results": 10
    }
    response = requests.post(f"{BASE_URL}/api/search/people", json=payload)
    print_response("4. Search People - 'Senior Software Engineer'", response)
    return response


# Test 5: Get Person by ID
def test_get_person():
    """GET /api/people/{person_id}"""
    # First, search to get a person ID
    search_response = requests.post(
        f"{BASE_URL}/api/search/people",
        json={"query": "engineer", "max_results": 1}
    )
    if search_response.status_code == 200:
        data = search_response.json()
        if data.get("results"):
            person_id = data["results"][0]["id"]
            response = requests.get(f"{BASE_URL}/api/people/{person_id}")
            print_response(f"5. Get Person by ID ({person_id})", response)
            return response
    print("Could not find a person ID to test")


# Test 6: List Companies
def test_list_companies():
    """GET /api/companies"""
    response = requests.get(f"{BASE_URL}/api/companies")
    print_response("6. List All Pakistani Companies", response)
    return response


# Test 7: Get Company by Name
def test_get_company():
    """GET /api/companies/{company_name}"""
    # First, get list of companies
    list_response = requests.get(f"{BASE_URL}/api/companies")
    if list_response.status_code == 200:
        companies = list_response.json().get("companies", [])
        if companies:
            company_name = companies[0]["account_name_profile"]
            response = requests.get(f"{BASE_URL}/api/companies/{company_name}")
            print_response(f"7. Get Company by Name ({company_name})", response)
            return response
    print("Could not find a company to test")


# Test 8: Match Company with People
def test_match_company():
    """POST /api/match/company"""
    payload = {
        "company_name": "DPL Technologies",
        "target_city": "Riyadh",
        "max_results": 5
    }
    response = requests.post(f"{BASE_URL}/api/match/company", json=payload)
    print_response("8. Match Company with People - DPL Technologies in Riyadh", response)
    return response


# Test 9: Match Company - Different Company
def test_match_company_different():
    """POST /api/match/company - Different company"""
    # Get a company name from the list
    list_response = requests.get(f"{BASE_URL}/api/companies")
    if list_response.status_code == 200:
        companies = list_response.json().get("companies", [])
        if companies:
            company_name = companies[0]["account_name_profile"]
            payload = {
                "company_name": company_name,
                "target_city": "Jeddah",
                "max_results": 3
            }
            response = requests.post(f"{BASE_URL}/api/match/company", json=payload)
            print_response(f"9. Match Company - {company_name} in Jeddah", response)
            return response


# Test 10: Save Query
def test_save_query():
    """POST /api/queries/save"""
    payload = {
        "query": "CTO in Saudi Arabia",
        "name": "CTO Search",
        "query_type": "people_search"
    }
    response = requests.post(f"{BASE_URL}/api/queries/save", json=payload)
    print_response("10. Save Query", response)
    return response


# Test 11: List Queries
def test_list_queries():
    """GET /api/queries"""
    response = requests.get(f"{BASE_URL}/api/queries")
    print_response("11. List All Saved Queries", response)
    return response


# Test 12: Get Query by ID
def test_get_query():
    """GET /api/queries/{query_id}"""
    list_response = requests.get(f"{BASE_URL}/api/queries")
    if list_response.status_code == 200:
        queries = list_response.json().get("queries", [])
        if queries:
            query_id = queries[0]["id"]
            response = requests.get(f"{BASE_URL}/api/queries/{query_id}")
            print_response(f"12. Get Query by ID ({query_id})", response)
            return response


# Test 13: Rename Query
def test_rename_query():
    """PUT /api/queries/{query_id}/rename"""
    list_response = requests.get(f"{BASE_URL}/api/queries")
    if list_response.status_code == 200:
        queries = list_response.json().get("queries", [])
        if queries:
            query_id = queries[0]["id"]
            payload = {"new_name": "Updated CTO Search"}
            response = requests.put(
                f"{BASE_URL}/api/queries/{query_id}/rename",
                json=payload
            )
            print_response(f"13. Rename Query ({query_id})", response)
            return response


# Test 14: Get Scoring Weights
def test_get_scoring_weights():
    """GET /api/scoring/weights"""
    response = requests.get(f"{BASE_URL}/api/scoring/weights")
    print_response("14. Get Current Scoring Weights", response)
    return response


# Test 15: Update Scoring Weights
def test_update_scoring_weights():
    """PUT /api/scoring/weights"""
    payload = {
        "industry_alignment": 0.35,
        "role_relevance": 0.30,
        "location_proximity": 0.20,
        "profile_completeness": 0.15
    }
    response = requests.put(f"{BASE_URL}/api/scoring/weights", json=payload)
    print_response("15. Update Scoring Weights", response)
    return response


# Test 16: Delete Query
def test_delete_query():
    """DELETE /api/queries/{query_id}"""
    list_response = requests.get(f"{BASE_URL}/api/queries")
    if list_response.status_code == 200:
        queries = list_response.json().get("queries", [])
        if queries:
            query_id = queries[-1]["id"]  # Delete last one
            response = requests.delete(f"{BASE_URL}/api/queries/{query_id}")
            print_response(f"16. Delete Query ({query_id})", response)
            return response


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING ALL API TESTS")
    print("="*60)
    
    try:
        test_health_check()
        test_root()
        test_search_people()
        test_search_people_different()
        test_get_person()
        test_list_companies()
        test_get_company()
        test_match_company()
        test_match_company_different()
        test_save_query()
        test_list_queries()
        test_get_query()
        test_rename_query()
        test_get_scoring_weights()
        test_update_scoring_weights()
        test_delete_query()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to the API.")
        print("Make sure the server is running:")
        print("  uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"\nERROR: {str(e)}")


if __name__ == "__main__":
    run_all_tests()







