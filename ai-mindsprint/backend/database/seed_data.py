"""
Seed data script for initializing the database with sample data
Run this after creating tables in Supabase
"""
from config import get_supabase_client
import json

def seed_skills():
    """Seed initial skills"""
    supabase = get_supabase_client()
    
    skills = [
        {
            "name": "Backend Development",
            "slug": "backend",
            "description": "Learn backend development with various technologies",
            "category": "Backend",
            "roadmap_id": "backend",
            "difficulty_level": "beginner",
            "estimated_duration_days": 90,
            "is_active": True
        },
        {
            "name": "Frontend Development",
            "slug": "frontend",
            "description": "Master frontend development and modern frameworks",
            "category": "Frontend",
            "roadmap_id": "frontend",
            "difficulty_level": "beginner",
            "estimated_duration_days": 90,
            "is_active": True
        },
        {
            "name": "DevOps",
            "slug": "devops",
            "description": "Learn DevOps practices and tools",
            "category": "DevOps",
            "roadmap_id": "devops",
            "difficulty_level": "intermediate",
            "estimated_duration_days": 120,
            "is_active": True
        },
        {
            "name": "AI & Machine Learning",
            "slug": "ai",
            "description": "Explore artificial intelligence and machine learning",
            "category": "AI",
            "roadmap_id": "ai",
            "difficulty_level": "advanced",
            "estimated_duration_days": 180,
            "is_active": True
        },
        {
            "name": "Database Administration",
            "slug": "databases",
            "description": "Master database design and administration",
            "category": "Databases",
            "roadmap_id": "databases",
            "difficulty_level": "intermediate",
            "estimated_duration_days": 90,
            "is_active": True
        }
    ]
    
    for skill in skills:
        # Check if exists
        existing = supabase.table("skills").select("*").eq("slug", skill["slug"]).execute()
        if not existing.data:
            supabase.table("skills").insert(skill).execute()
            print(f"✓ Seeded skill: {skill['name']}")


def seed_badges():
    """Seed initial badges"""
    supabase = get_supabase_client()
    
    badges = [
        {
            "name": "First Steps",
            "description": "Complete your first task",
            "badge_type": "achievement",
            "points_required": 10,
            "criteria": {"tasks_completed": 1},
            "is_active": True
        },
        {
            "name": "Week Warrior",
            "description": "Maintain a 7-day streak",
            "badge_type": "streak",
            "points_required": 0,
            "criteria": {"days": 7},
            "is_active": True
        },
        {
            "name": "Month Master",
            "description": "Maintain a 30-day streak",
            "badge_type": "streak",
            "points_required": 0,
            "criteria": {"days": 30},
            "is_active": True
        },
        {
            "name": "Point Collector",
            "description": "Earn 100 points",
            "badge_type": "points",
            "points_required": 100,
            "criteria": {},
            "is_active": True
        },
        {
            "name": "Centurion",
            "description": "Earn 1000 points",
            "badge_type": "points",
            "points_required": 1000,
            "criteria": {},
            "is_active": True
        },
        {
            "name": "Skill Master",
            "description": "Complete a skill learning path",
            "badge_type": "skill_completion",
            "points_required": 0,
            "criteria": {"progress": 100},
            "is_active": True
        }
    ]
    
    for badge in badges:
        existing = supabase.table("badges").select("*").eq("name", badge["name"]).execute()
        if not existing.data:
            supabase.table("badges").insert(badge).execute()
            print(f"✓ Seeded badge: {badge['name']}")


def seed_sample_mcqs():
    """Seed sample MCQs for testing"""
    supabase = get_supabase_client()
    
    # Get backend skill
    backend_skill = supabase.table("skills").select("id").eq("slug", "backend").execute()
    if not backend_skill.data:
        print("⚠ Backend skill not found. Please seed skills first.")
        return
    
    skill_id = backend_skill.data[0]["id"]
    
    mcqs = [
        {
            "skill_id": skill_id,
            "question": "What does HTTP stand for?",
            "options": [
                {"id": 1, "text": "HyperText Transfer Protocol"},
                {"id": 2, "text": "High Transfer Text Protocol"},
                {"id": 3, "text": "HyperText Transmission Protocol"},
                {"id": 4, "text": "Hyper Transfer Text Protocol"}
            ],
            "correct_answer_id": 1,
            "explanation": "HTTP stands for HyperText Transfer Protocol, the foundation of data communication on the web.",
            "difficulty": "beginner",
            "points": 1,
            "is_active": True
        },
        {
            "skill_id": skill_id,
            "question": "What is the default port for HTTP?",
            "options": [
                {"id": 1, "text": "80"},
                {"id": 2, "text": "443"},
                {"id": 3, "text": "8080"},
                {"id": 4, "text": "3000"}
            ],
            "correct_answer_id": 1,
            "explanation": "Port 80 is the default port for HTTP. Port 443 is for HTTPS.",
            "difficulty": "beginner",
            "points": 1,
            "is_active": True
        },
        {
            "skill_id": skill_id,
            "question": "What is REST?",
            "options": [
                {"id": 1, "text": "Representational State Transfer"},
                {"id": 2, "text": "Remote State Transfer"},
                {"id": 3, "text": "Representational Server Transfer"},
                {"id": 4, "text": "Remote Server Transfer"}
            ],
            "correct_answer_id": 1,
            "explanation": "REST stands for Representational State Transfer, an architectural style for designing web services.",
            "difficulty": "intermediate",
            "points": 2,
            "is_active": True
        }
    ]
    
    for mcq in mcqs:
        existing = supabase.table("mcqs").select("*").eq("question", mcq["question"]).execute()
        if not existing.data:
            supabase.table("mcqs").insert(mcq).execute()
            print(f"✓ Seeded MCQ: {mcq['question'][:50]}...")


if __name__ == "__main__":
    print("Seeding database...")
    print("-" * 50)
    seed_skills()
    print("-" * 50)
    seed_badges()
    print("-" * 50)
    seed_sample_mcqs()
    print("-" * 50)
    print("✓ Database seeding complete!")

