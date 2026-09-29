"""
User API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import UserCreate, UserResponse
from config import get_supabase_client
from services.roadmap_service import RoadmapService
from services.task_assignment_service import TaskAssignmentService
from services.rewards_service import RewardsService
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user and assign initial tasks"""
    supabase = get_supabase_client()
    
    # Check if user already exists
    existing = supabase.table("users").select("*").eq("email", user_data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user (in production, this would integrate with Supabase Auth)
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "phone_number": user_data.phone_number,
        "role": "learner",
        "current_level": "beginner",
        "total_points": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "is_active": True
    }
    
    result = supabase.table("users").insert(user).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create notification settings
    supabase.table("notification_settings").insert({
        "user_id": user_id
    }).execute()
    
    # Process selected skills
    roadmap_service = RoadmapService()
    task_service = TaskAssignmentService()
    
    for skill_slug in user_data.selected_skills:
        # Get or create skill
        skill = supabase.table("skills").select("*").eq("slug", skill_slug).execute()
        if not skill.data:
            # Create skill if doesn't exist
            skill_data = {
                "name": skill_slug.title(),
                "slug": skill_slug,
                "category": skill_slug,
                "roadmap_id": skill_slug
            }
            skill_result = supabase.table("skills").insert(skill_data).execute()
            skill_id = skill_result.data[0]["id"] if skill_result.data else None
        else:
            skill_id = skill.data[0]["id"]
        
        if skill_id:
            # Link user to skill
            supabase.table("user_skills").insert({
                "user_id": user_id,
                "skill_id": skill_id,
                "status": "in_progress"
            }).execute()
            
            # Fetch roadmap and create tasks
            roadmap = await roadmap_service.get_roadmap(skill_slug)
            if roadmap:
                # Store roadmap
                roadmap_data = {
                    "skill_id": skill_id,
                    "roadmap_data": roadmap,
                    "title": roadmap.get("title", ""),
                    "description": roadmap.get("description", ""),
                    "total_milestones": len(roadmap.get("milestones", [])),
                    "source": "roadmap.sh"
                }
                roadmap_result = supabase.table("roadmaps").insert(roadmap_data).execute()
                roadmap_id = roadmap_result.data[0]["id"] if roadmap_result.data else None
                
                # Convert roadmap to tasks
                tasks = roadmap_service.convert_roadmap_to_tasks(roadmap, skill_id)
                for task in tasks:
                    if roadmap_id:
                        task["roadmap_id"] = roadmap_id
                    supabase.table("tasks").insert(task).execute()
            
            # Assign initial tasks
            await task_service.assign_initial_tasks(user_id, skill_id)
    
    return result.data[0]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    supabase = get_supabase_client()
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    return user.data[0]


@router.get("/{user_id}/skills")
async def get_user_skills(user_id: str):
    """Get all skills for a user"""
    supabase = get_supabase_client()
    user_skills = supabase.table("user_skills").select("*, skills(*)").eq("user_id", user_id).execute()
    return {"skills": user_skills.data}


@router.get("/{user_id}/dashboard")
async def get_user_dashboard(user_id: str):
    """Get user dashboard data"""
    supabase = get_supabase_client()
    
    # Get user
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get active tasks
    tasks = supabase.table("task_assignments").select("*, tasks(*)").eq("user_id", user_id).in_("status", ["pending", "in_progress"]).order("due_date").limit(10).execute()
    
    # Get recent badges
    badges = supabase.table("user_badges").select("*, badges(*)").eq("user_id", user_id).order("earned_at", desc=True).limit(5).execute()
    
    # Get rewards summary
    rewards_service = RewardsService()
    rewards = await rewards_service.get_user_rewards_summary(user_id)
    
    return {
        "user": user.data[0],
        "active_tasks": tasks.data,
        "recent_badges": [b.get("badges", {}) for b in badges.data],
        "rewards": rewards
    }

