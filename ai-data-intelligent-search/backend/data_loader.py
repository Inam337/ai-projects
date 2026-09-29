import csv
import json
import os
from typing import List, Dict, Optional
from models import Person, Company
from deduplication import DeduplicationEngine

# Try to import pandas and tqdm for optimized loading
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Install pandas for faster CSV loading: pip install pandas")

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback: create a dummy tqdm that just returns the iterable
    def tqdm(iterable, **kwargs):
        return iterable


class DataLoader:
    """Load and manage datasets"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to datasets folder relative to backend directory
            import os
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(backend_dir, "datasets")
        else:
            self.data_dir = data_dir
        self.people: List[Person] = []
        self.companies: List[Company] = []
        self.pakistani_companies: List[Company] = []
        self.people_by_id: Dict[str, Person] = {}
        self.companies_by_id: Dict[str, Company] = {}
        self.pakistani_companies_by_name: Dict[str, Company] = {}
    
    def load_people_dataset(self, filename: str = "dataset_a_people.csv") -> List[Person]:
        """Load people dataset (Dataset A) - Optimized for large datasets"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return []
        
        print(f"Loading {filename}...")
        
        # Use pandas for fast CSV reading (much faster than csv.DictReader)
        if not PANDAS_AVAILABLE:
            print("Pandas not available, using csv.DictReader fallback")
            return self._load_people_dataset_fallback(filepath)
        
        try:
            # Read CSV in chunks for very large files, but process all at once for speed
            df = pd.read_csv(filepath, encoding='utf-8', low_memory=False, dtype=str)
            print(f"CSV loaded: {len(df)} rows")
        except Exception as e:
            print(f"Error reading CSV with pandas, falling back to csv.DictReader: {e}")
            # Fallback to original method
            return self._load_people_dataset_fallback(filepath)
        
        people = []
        total_rows = len(df)
        
        # Process rows with progress indicator
        for idx, row in tqdm(df.iterrows(), total=total_rows, desc="Processing people"):
            try:
                # Generate ID from salesNavigatorId (convert SN to P) or index
                sales_nav_id = str(row.get('salesNavigatorId', '')) if pd.notna(row.get('salesNavigatorId')) else ''
                if sales_nav_id and sales_nav_id.startswith('SN'):
                    # Convert SN000001 to P00001
                    person_id = 'P' + sales_nav_id[2:]
                else:
                    person_id = f'P{idx+1:05d}'
                
                # Map account_name_profile to current_company for Person model
                current_company = str(row.get('account_name_profile', '')) if pd.notna(row.get('account_name_profile')) else ''
                if not current_company:
                    current_company = str(row.get('current_company', '')) if pd.notna(row.get('current_company')) else ''
                
                # Parse employee_count and founded_year as integers
                employee_count = None
                emp_val = row.get('employee_count')
                if pd.notna(emp_val) and str(emp_val).strip():
                    try:
                        employee_count = int(float(str(emp_val)))
                    except:
                        pass
                
                founded_year = None
                found_val = row.get('founded_year')
                if pd.notna(found_val) and str(found_val).strip():
                    try:
                        founded_year = int(float(str(found_val)))
                    except:
                        pass
                
                # Helper function to safely get string values
                def safe_str(val):
                    return str(val) if pd.notna(val) else None
                
                def safe_str_or_empty(val):
                    return str(val) if pd.notna(val) else ''
                
                person = Person(
                    id=person_id,
                    firstName=safe_str_or_empty(row.get('firstName', '')),
                    lastName=safe_str_or_empty(row.get('lastName', '')),
                    gender=safe_str(row.get('gender')),
                    job_title=safe_str(row.get('job_title')),
                    headline=safe_str(row.get('headline')),
                    location=safe_str(row.get('location')),
                    linkedinUrl=safe_str(row.get('linkedinUrl')),
                    profilePictureUrl=safe_str(row.get('profilePictureUrl')),
                    importDate=safe_str(row.get('importDate')),
                    premium=safe_str(row.get('premium')),
                    jobSeeker=safe_str(row.get('jobSeeker')),
                    salesNavigatorId=safe_str(row.get('salesNavigatorId')),
                    current_company=current_company,
                    industry=safe_str(row.get('industry')),
                    seniority=None,  # Not in new CSV structure
                    education=None,  # Not in new CSV structure
                    # Company-related fields from dataset_a_people.csv
                    account_name_profile=safe_str(row.get('account_name_profile')),
                    account_name_clean=safe_str(row.get('account_name_clean')),
                    website=safe_str(row.get('website')),
                    linkedin_url=safe_str(row.get('linkedin_url')),
                    facebook_url=safe_str(row.get('facebook_url')),
                    twitter_url=safe_str(row.get('twitter_url')),
                    account_city=safe_str(row.get('account_city')),
                    account_state=safe_str(row.get('account_state')),
                    account_country=safe_str(row.get('account_country')),
                    postal_code=safe_str(row.get('postal_code')),
                    account_address=safe_str(row.get('account_address')),
                    keywords=safe_str(row.get('keywords')),
                    account_phone=safe_str(row.get('account_phone')),
                    technologies=safe_str(row.get('technologies')),
                    annual_revenue=safe_str(row.get('annual_revenue')),
                    sic_code=safe_str(row.get('sic_code')),
                    naics_code=safe_str(row.get('naics_code')),
                    account_description=safe_str(row.get('account_description')),
                    founded_year=founded_year,
                    logo_url=safe_str(row.get('logo_url')),
                    subsidiary_of=safe_str(row.get('subsidiary_of')),
                    employee_count=employee_count
                )
                person.profile_completeness = person.calculate_completeness()
                people.append(person)
                self.people_by_id[person.id] = person
            except Exception as e:
                print(f"Error loading person {idx}: {e}")
                continue
        
        print(f"Loaded {len(people)} people records")
        
        # Deduplicate people records with optimized algorithm
        print("Deduplicating records...")
        dedup_engine = DeduplicationEngine(similarity_threshold=0.85)
        deduplicated_people, merge_map = dedup_engine.deduplicate_optimized(people)
        
        stats = dedup_engine.get_deduplication_stats(len(people), len(deduplicated_people))
        print(f"Deduplication: {stats['original_count']} → {stats['deduplicated_count']} "
              f"({stats['reduction_percent']}% reduction)")
        
        self.people = deduplicated_people
        # Rebuild ID map after deduplication
        self.people_by_id = {p.id: p for p in deduplicated_people}
        
        return deduplicated_people
    
    def _load_people_dataset_fallback(self, filepath: str) -> List[Person]:
        """Fallback method using csv.DictReader if pandas fails"""
        people = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                try:
                    # Generate ID from salesNavigatorId (convert SN to P) or index
                    sales_nav_id = row.get('salesNavigatorId', '')
                    if sales_nav_id and sales_nav_id.startswith('SN'):
                        person_id = 'P' + sales_nav_id[2:]
                    else:
                        person_id = f'P{idx+1:05d}'
                    
                    current_company = row.get('account_name_profile', '') or row.get('current_company', '')
                    
                    employee_count = None
                    if row.get('employee_count'):
                        try:
                            employee_count = int(row['employee_count'])
                        except:
                            pass
                    
                    founded_year = None
                    if row.get('founded_year'):
                        try:
                            founded_year = int(row['founded_year'])
                        except:
                            pass
                    
                    person = Person(
                        id=person_id,
                        firstName=row.get('firstName', ''),
                        lastName=row.get('lastName', ''),
                        gender=row.get('gender'),
                        job_title=row.get('job_title'),
                        headline=row.get('headline'),
                        location=row.get('location'),
                        linkedinUrl=row.get('linkedinUrl'),
                        profilePictureUrl=row.get('profilePictureUrl'),
                        importDate=row.get('importDate'),
                        premium=row.get('premium'),
                        jobSeeker=row.get('jobSeeker'),
                        salesNavigatorId=row.get('salesNavigatorId'),
                        current_company=current_company,
                        industry=row.get('industry'),
                        seniority=None,
                        education=None,
                        account_name_profile=row.get('account_name_profile'),
                        account_name_clean=row.get('account_name_clean'),
                        website=row.get('website'),
                        linkedin_url=row.get('linkedin_url'),
                        facebook_url=row.get('facebook_url'),
                        twitter_url=row.get('twitter_url'),
                        account_city=row.get('account_city'),
                        account_state=row.get('account_state'),
                        account_country=row.get('account_country'),
                        postal_code=row.get('postal_code'),
                        account_address=row.get('account_address'),
                        keywords=row.get('keywords'),
                        account_phone=row.get('account_phone'),
                        technologies=row.get('technologies'),
                        annual_revenue=row.get('annual_revenue'),
                        sic_code=row.get('sic_code'),
                        naics_code=row.get('naics_code'),
                        account_description=row.get('account_description'),
                        founded_year=founded_year,
                        logo_url=row.get('logo_url'),
                        subsidiary_of=row.get('subsidiary_of'),
                        employee_count=employee_count
                    )
                    person.profile_completeness = person.calculate_completeness()
                    people.append(person)
                    self.people_by_id[person.id] = person
                except Exception as e:
                    print(f"Error loading person {idx}: {e}")
                    continue
        
        dedup_engine = DeduplicationEngine(similarity_threshold=0.85)
        deduplicated_people, merge_map = dedup_engine.deduplicate_optimized(people)
        
        stats = dedup_engine.get_deduplication_stats(len(people), len(deduplicated_people))
        print(f"Deduplication: {stats['original_count']} → {stats['deduplicated_count']} "
              f"({stats['reduction_percent']}% reduction)")
        
        self.people = deduplicated_people
        self.people_by_id = {p.id: p for p in deduplicated_people}
        
        return deduplicated_people
    
    def load_companies_dataset(self, filename: str = "dataset_a_companies.csv") -> List[Company]:
        """Load companies dataset (Dataset A - people companies)"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return []
        
        companies = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                try:
                    employee_count = None
                    if row.get('employee_count'):
                        try:
                            employee_count = int(row['employee_count'])
                        except:
                            pass
                    
                    founded_year = None
                    if row.get('founded_year'):
                        try:
                            founded_year = int(row['founded_year'])
                        except:
                            pass
                    
                    company = Company(
                        id=row.get('id', str(idx)),
                        account_name_profile=row.get('account_name_profile', ''),
                        account_name_clean=row.get('account_name_clean'),
                        website=row.get('website'),
                        linkedin_url=row.get('linkedin_url'),
                        facebook_url=row.get('facebook_url'),
                        twitter_url=row.get('twitter_url'),
                        account_phone=row.get('account_phone'),
                        employee_count=employee_count,
                        industry=row.get('industry'),
                        account_city=row.get('account_city'),
                        account_state=row.get('account_state'),
                        account_country=row.get('account_country'),
                        account_description=row.get('account_description'),
                        technologies=row.get('technologies'),
                        keywords=row.get('keywords'),
                        postal_code=row.get('postal_code'),
                        account_address=row.get('account_address'),
                        subsidiary_of=row.get('subsidiary_of'),
                        founded_year=founded_year,
                        annual_revenue=row.get('annual_revenue'),
                        sic_code=row.get('sic_code'),
                        naics_code=row.get('naics_code'),
                        logo_url=row.get('logo_url')
                    )
                    companies.append(company)
                    self.companies_by_id[company.id] = company
                except Exception as e:
                    print(f"Error loading company {idx}: {e}")
                    continue
        
        self.companies = companies
        return companies
    
    def load_pakistani_companies_dataset(self, filename: str = "dataset_b_pakistani_companies.csv") -> List[Company]:
        """Load Pakistani companies dataset (Dataset B)"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return []
        
        companies = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                try:
                    # Generate ID from index (no id column in new structure)
                    company_id = f'C{idx+1:03d}'
                    
                    employee_count = None
                    if row.get('employee_count'):
                        try:
                            employee_count = int(row['employee_count'])
                        except:
                            pass
                    
                    founded_year = None
                    if row.get('founded_year'):
                        try:
                            founded_year = int(row['founded_year'])
                        except:
                            pass
                    
                    company = Company(
                        id=company_id,
                        account_name_profile=row.get('account_name_profile', ''),
                        account_name_clean=row.get('account_name_profile', ''),  # Use account_name_profile as clean
                        website=row.get('website'),
                        linkedin_url=row.get('linkedin_url'),
                        facebook_url=row.get('facebook_url'),
                        twitter_url=row.get('twitter_url'),
                        account_phone=row.get('account_phone'),
                        employee_count=employee_count,
                        industry=row.get('industry'),
                        account_city=row.get('account_city'),
                        account_state=row.get('account_state'),
                        account_country=row.get('account_country'),
                        account_description=row.get('account_description'),
                        technologies=row.get('technologies'),
                        keywords=row.get('keywords'),
                        account_services=row.get('account_services'),
                        postal_code=row.get('postal_code'),
                        account_address=row.get('account_address'),
                        subsidiary_of=None,  # Not in new CSV structure
                        founded_year=founded_year,
                        annual_revenue=row.get('annual_revenue'),
                        sic_code=row.get('sic_code'),
                        naics_code=row.get('naics_code'),
                        logo_url=None  # Not in new CSV structure
                    )
                    companies.append(company)
                    self.pakistani_companies_by_name[company.account_name_clean or company.account_name_profile] = company
                except Exception as e:
                    print(f"Error loading Pakistani company {idx}: {e}")
                    continue
        
        self.pakistani_companies = companies
        return companies
    
    def load_all(self):
        """Load all datasets"""
        self.load_people_dataset()
        self.load_companies_dataset()
        self.load_pakistani_companies_dataset()
        print(f"Loaded {len(self.people)} people, {len(self.companies)} companies, {len(self.pakistani_companies)} Pakistani companies")
    
    def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Get person by ID"""
        return self.people_by_id.get(person_id)
    
    def get_pakistani_company_by_name(self, name: str) -> Optional[Company]:
        """Get Pakistani company by name (fuzzy matching)"""
        name_lower = name.lower().strip()
        # Exact match
        for company_name, company in self.pakistani_companies_by_name.items():
            if company_name.lower() == name_lower:
                return company
        # Partial match
        for company_name, company in self.pakistani_companies_by_name.items():
            if name_lower in company_name.lower() or company_name.lower() in name_lower:
                return company
        return None

