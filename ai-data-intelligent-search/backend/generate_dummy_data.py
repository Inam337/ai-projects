import csv
import random
import os
from datetime import datetime, timedelta


def generate_dummy_people_dataset(filename: str = "dataset_a_people.csv", num_records: int = 1000):
    """Generate dummy people dataset (Dataset A)"""
    
    first_names = [
        "Ahmed", "Muhammad", "Ali", "Hassan", "Usman", "Omar", "Khalid", "Fahad", "Saeed", "Ibrahim",
        "Fatima", "Aisha", "Maryam", "Zainab", "Khadija", "Amina", "Hafsa", "Sara", "Noor", "Layla",
        "John", "David", "Michael", "Robert", "James", "William", "Richard", "Joseph", "Thomas", "Charles",
        "Sarah", "Jennifer", "Emily", "Jessica", "Amanda", "Lisa", "Michelle", "Patricia", "Linda", "Barbara"
    ]
    
    last_names = [
        "Al-Saud", "Al-Rashid", "Al-Mansouri", "Al-Zahrani", "Al-Otaibi", "Al-Mutairi", "Al-Harbi", "Al-Ghamdi",
        "Khan", "Ali", "Ahmed", "Hassan", "Malik", "Sheikh", "Butt", "Raza", "Iqbal", "Hussain", "Shah",
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ]
    
    job_titles = [
        "Chief Technology Officer", "Chief Information Officer", "IT Director", "Senior Software Engineer",
        "Project Manager", "Business Analyst", "Data Scientist", "Cloud Architect", "DevOps Engineer",
        "IT Consultant", "Software Developer", "Systems Administrator", "Network Engineer", "Database Administrator",
        "Security Specialist", "Product Manager", "Technical Lead", "Engineering Manager", "Solutions Architect"
    ]
    
    industries = [
        "IT Services", "Software Development", "Cloud Computing", "Cybersecurity", "Data Analytics",
        "ERP Solutions", "Digital Transformation", "Fintech", "E-commerce", "Healthcare IT",
        "Oil & Energy", "Banking", "Telecommunications", "Retail", "Manufacturing"
    ]
    
    locations = [
        "Riyadh, Saudi Arabia", "Jeddah, Saudi Arabia", "Dammam, Saudi Arabia", "Khobar, Saudi Arabia",
        "Mecca, Saudi Arabia", "Medina, Saudi Arabia", "Karachi, Pakistan", "Lahore, Pakistan",
        "Islamabad, Pakistan", "Dubai, UAE", "Abu Dhabi, UAE"
    ]
    
    seniority_levels = ["Entry", "Mid", "Senior", "Lead", "Principal", "Director", "VP", "C-Level"]
    
    genders = ["Male", "Female", "Unspecified"]
    
    headlines = [
        "Experienced IT professional specializing in cloud solutions",
        "Software engineer with expertise in enterprise applications",
        "IT consultant helping businesses digital transformation",
        "Technology leader driving innovation",
        "Data scientist passionate about analytics",
        "Cybersecurity expert protecting digital assets",
        "ERP implementation specialist",
        "DevOps engineer automating infrastructure",
        "Full-stack developer building scalable applications",
        "IT director managing technology teams"
    ]
    
    companies = [
        "Saudi Telecom Company", "Aramco", "SABIC", "Al Rajhi Bank", "NCB Bank",
        "STC Solutions", "IBM Saudi Arabia", "Microsoft Saudi Arabia", "Oracle Saudi Arabia",
        "Accenture", "Deloitte", "PwC", "Ernst & Young", "KPMG",
        "TechCorp Solutions", "Digital Ventures", "Cloud Systems", "Data Analytics Pro",
        "SecureNet", "IT Innovations", "Enterprise Solutions", "Modern Tech"
    ]
    
    os.makedirs("datasets", exist_ok=True)
    
    with open(f"datasets/{filename}", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'firstName', 'lastName', 'gender', 'job_title', 'headline', 'location',
            'linkedinUrl', 'profilePictureUrl', 'importDate', 'premium', 'jobSeeker',
            'salesNavigatorId', 'current_company', 'industry', 'seniority', 'education'
        ])
        
        for i in range(num_records):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            job_title = random.choice(job_titles)
            industry = random.choice(industries)
            location = random.choice(locations)
            seniority = random.choice(seniority_levels)
            gender = random.choice(genders)
            headline = random.choice(headlines)
            company = random.choice(companies)
            
            # Generate LinkedIn URL
            linkedin_url = f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{i}"
            
            # Generate profile picture URL (dummy)
            profile_pic = f"https://example.com/profiles/{first_name.lower()}_{last_name.lower()}_{i}.jpg"
            
            # Generate import date (random date in last 6 months)
            import_date = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
            
            # Premium status
            premium = "Yes" if random.random() < 0.1 else "No"
            
            # Job seeker status
            job_seeker = "Yes" if random.random() < 0.15 else "No"
            
            # Education (sometimes missing)
            education = None
            if random.random() > 0.3:
                education = random.choice([
                    "BS Computer Science, King Saud University",
                    "MS Information Technology, MIT",
                    "MBA, INSEAD",
                    "BS Software Engineering, NUST",
                    "MS Data Science, Stanford"
                ])
            
            writer.writerow([
                f"P{i+1:05d}",
                first_name,
                last_name,
                gender,
                job_title,
                headline,
                location,
                linkedin_url,
                profile_pic,
                import_date,
                premium,
                job_seeker,
                f"SN{i+1:06d}",
                company,
                industry,
                seniority,
                education
            ])
    
    print(f"Generated {num_records} dummy people records in {filepath}")


def generate_dummy_pakistani_companies_dataset(filename: str = "dataset_b_pakistani_companies.csv", num_records: int = 50):
    """Generate dummy Pakistani IT companies dataset (Dataset B)"""
    
    company_names = [
        "DPL Technologies", "TechSolutions Pakistan", "Digital Innovations PK", "PakSoft Systems",
        "IT Solutions Pakistan", "CloudTech Pakistan", "DataSync Pakistan", "ERP Masters Pakistan",
        "CyberSec Pakistan", "DevOps Pakistan", "AIOps Pakistan", "FinTech Pakistan",
        "HealthTech Pakistan", "EduTech Pakistan", "AgriTech Pakistan", "LogiTech Pakistan",
        "RetailTech Pakistan", "RealEstateTech Pakistan", "HRTech Pakistan", "MarketingTech Pakistan"
    ]
    
    industries = [
        "IT Services", "Software Development", "Cloud Computing", "Cybersecurity",
        "ERP Solutions", "Digital Transformation", "Fintech", "E-commerce", "Healthcare IT"
    ]
    
    services = [
        "Enterprise Software Development", "Cloud Migration Services", "ERP Implementation",
        "Digital Transformation Consulting", "Mobile App Development", "Web Development",
        "Data Analytics Solutions", "Cybersecurity Services", "IT Infrastructure Management",
        "Software Testing & QA", "DevOps Consulting", "AI/ML Solutions"
    ]
    
    technologies = [
        "Python, Java, .NET, React, Angular", "AWS, Azure, Google Cloud", "Oracle, SAP, Microsoft Dynamics",
        "Docker, Kubernetes, Jenkins", "MySQL, PostgreSQL, MongoDB", "React Native, Flutter",
        "TensorFlow, PyTorch", "Salesforce, HubSpot", "Git, JIRA, Confluence"
    ]
    
    cities = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad"]
    states = ["Sindh", "Punjab", "Islamabad Capital Territory", "Khyber Pakhtunkhwa"]
    
    # Get backend directory and create datasets folder
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(backend_dir, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)
    
    filepath = os.path.join(datasets_dir, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'account_name_profile', 'account_name_clean', 'website', 'linkedin_url',
            'facebook_url', 'twitter_url', 'account_phone', 'employee_count', 'industry',
            'account_city', 'account_state', 'account_country', 'account_description',
            'technologies', 'keywords', 'account_services', 'postal_code', 'account_address',
            'subsidiary_of', 'founded_year', 'annual_revenue', 'sic_code', 'naics_code', 'logo_url'
        ])
        
        for i in range(num_records):
            name = random.choice(company_names) if i < len(company_names) else f"Tech Company {i+1}"
            industry = random.choice(industries)
            service = random.choice(services)
            tech = random.choice(technologies)
            city = random.choice(cities)
            state = random.choice(states)
            
            employee_count = random.choice([10, 25, 50, 100, 200, 500, 1000])
            founded_year = random.randint(2010, 2023)
            
            website = f"https://www.{name.lower().replace(' ', '')}.com"
            linkedin_url = f"https://www.linkedin.com/company/{name.lower().replace(' ', '-')}"
            
            description = f"{name} provides {service.lower()} in the {industry} sector."
            
            keywords = f"{industry}, {service}, Pakistan, IT Services"
            
            annual_revenue = random.choice([
                "$1M - $5M", "$5M - $10M", "$10M - $50M", "$50M - $100M", "Not disclosed"
            ])
            
            logo_url = f"https://example.com/logos/{name.lower().replace(' ', '_')}.png"
            
            writer.writerow([
                f"C{i+1:03d}",
                name,
                name.replace(" Inc.", "").replace(" LLC", "").replace(" Ltd.", ""),
                website,
                linkedin_url,
                f"https://facebook.com/{name.lower().replace(' ', '')}",
                f"https://twitter.com/{name.lower().replace(' ', '')}",
                f"+92-{random.randint(300, 399)}-{random.randint(1000000, 9999999)}",
                employee_count,
                industry,
                city,
                state,
                "Pakistan",
                description,
                tech,
                keywords,
                service,
                f"{random.randint(10000, 99999)}",
                f"{city}, {state}, Pakistan",
                None,
                founded_year,
                annual_revenue,
                f"{random.randint(7000, 8000)}",
                f"{random.randint(500000, 600000)}",
                logo_url
            ])
    
    print(f"Generated {num_records} dummy Pakistani company records in {filepath}")


if __name__ == "__main__":
    print("Generating dummy datasets...")
    generate_dummy_people_dataset(num_records=1000)
    generate_dummy_pakistani_companies_dataset(num_records=50)
    print("Done!")

