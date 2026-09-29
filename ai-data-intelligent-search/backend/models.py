from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class Person(BaseModel):
    """Person profile model matching Dataset A requirements"""
    id: str
    firstName: str
    lastName: str
    gender: Optional[str] = None
    job_title: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    linkedinUrl: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    importDate: Optional[str] = None
    premium: Optional[str] = None
    jobSeeker: Optional[str] = None
    salesNavigatorId: Optional[str] = None
    current_company: Optional[str] = None
    industry: Optional[str] = None
    seniority: Optional[str] = None
    education: Optional[str] = None
    # Company-related fields from dataset_a_people.csv
    account_name_profile: Optional[str] = None
    account_name_clean: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None  # Company LinkedIn URL (different from linkedinUrl)
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    account_city: Optional[str] = None
    account_state: Optional[str] = None
    account_country: Optional[str] = None
    postal_code: Optional[str] = None
    account_address: Optional[str] = None
    keywords: Optional[str] = None
    account_phone: Optional[str] = None
    technologies: Optional[str] = None
    annual_revenue: Optional[str] = None
    sic_code: Optional[str] = None
    naics_code: Optional[str] = None
    account_description: Optional[str] = None
    founded_year: Optional[int] = None
    logo_url: Optional[str] = None
    subsidiary_of: Optional[str] = None
    employee_count: Optional[int] = None
    profile_completeness: float = 0.0
    
    def calculate_completeness(self) -> float:
        """Calculate profile completeness percentage"""
        fields = [
            self.firstName, self.lastName, self.job_title, self.headline,
            self.location, self.linkedinUrl, self.current_company,
            self.industry, self.seniority
        ]
        filled = sum(1 for field in fields if field and str(field).strip())
        return (filled / len(fields)) * 100
    
    def get_searchable_text(self) -> str:
        """Get all searchable text fields combined"""
        parts = [
            self.firstName or "",
            self.lastName or "",
            self.job_title or "",
            self.headline or "",
            self.location or "",
            self.current_company or "",
            self.industry or "",
            self.seniority or "",
            self.education or "",
            self.account_description or "",
            self.keywords or "",
            self.technologies or "",
            self.account_city or "",
            self.account_state or "",
            self.account_country or ""
        ]
        return " ".join(parts).lower()


class Company(BaseModel):
    """Company model matching Dataset A (people companies) and Dataset B (Pakistani companies)"""
    id: str
    account_name_profile: str
    account_name_clean: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    account_phone: Optional[str] = None
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    account_city: Optional[str] = None
    account_state: Optional[str] = None
    account_country: Optional[str] = None
    account_description: Optional[str] = None
    technologies: Optional[str] = None
    keywords: Optional[str] = None
    account_services: Optional[str] = None  # Only for Dataset B
    postal_code: Optional[str] = None
    account_address: Optional[str] = None
    subsidiary_of: Optional[str] = None
    founded_year: Optional[int] = None
    annual_revenue: Optional[str] = None
    sic_code: Optional[str] = None
    naics_code: Optional[str] = None
    logo_url: Optional[str] = None
    
    def get_searchable_text(self) -> str:
        """Get all searchable text fields combined"""
        parts = [
            self.account_name_profile or "",
            self.account_name_clean or "",
            self.industry or "",
            self.account_description or "",
            self.technologies or "",
            self.keywords or "",
            self.account_services or "",
            self.account_city or "",
            self.account_country or ""
        ]
        return " ".join(parts).lower()


class ScoreBreakdown(BaseModel):
    """Breakdown of scoring components"""
    industry_alignment: float
    role_relevance: float
    location_proximity: float
    profile_completeness: float
    total_score: float


class SearchResult(BaseModel):
    """Enhanced search result with scoring breakdown"""
    person: Person
    relevance_score: float
    score_breakdown: ScoreBreakdown
    explanation: str


class PersonProfile(BaseModel):
    """API response model for person profile"""
    id: str
    firstName: str
    lastName: str
    full_name: str
    job_title: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    current_company: Optional[str] = None
    seniority: Optional[str] = None
    gender: Optional[str] = None
    profilePictureUrl: Optional[str] = None
    linkedinUrl: Optional[str] = None
    # Additional fields from dataset
    account_name_profile: Optional[str] = None
    account_name_clean: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None  # Company LinkedIn URL
    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    account_city: Optional[str] = None
    account_state: Optional[str] = None
    account_country: Optional[str] = None
    postal_code: Optional[str] = None
    account_address: Optional[str] = None
    keywords: Optional[str] = None
    account_phone: Optional[str] = None
    technologies: Optional[str] = None
    annual_revenue: Optional[str] = None
    sic_code: Optional[str] = None
    naics_code: Optional[str] = None
    account_description: Optional[str] = None
    founded_year: Optional[int] = None
    logo_url: Optional[str] = None
    subsidiary_of: Optional[str] = None
    employee_count: Optional[int] = None
    importDate: Optional[str] = None
    premium: Optional[str] = None
    jobSeeker: Optional[str] = None
    salesNavigatorId: Optional[str] = None
    profile_completeness: Optional[float] = None
    relevance_score: Optional[float] = None
    explanation: Optional[str] = None


class SearchResults(BaseModel):
    """API response model for search results"""
    query: str
    results: List[PersonProfile]
    total_results: int


class CompanyMatchQuery(BaseModel):
    """API request model for company matchmaking"""
    company_name: str
    target_city: Optional[str] = None
    max_results: Optional[int] = 5


class CompanyMatchResult(BaseModel):
    """API response model for company matchmaking results"""
    company_name: str
    matched_professionals: List[PersonProfile]
    matching_criteria: str

