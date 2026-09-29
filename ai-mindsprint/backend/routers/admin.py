"""
Admin API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import SkillCreate, TaskCreate, HandoutCreate, MCQCreate, NotificationSettingsUpdate
from config import get_supabase_client
from services.notification_service import NotificationService
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard statistics"""
    supabase = get_supabase_client()
    
    # Get user statistics
    users = supabase.table("users").select("id, current_level, total_points, current_streak").execute()
    total_users = len(users.data)
    
    # Get task statistics
    tasks = supabase.table("task_assignments").select("status").execute()
    completed_tasks = len([t for t in tasks.data if t.get("status") == "completed"])
    pending_tasks = len([t for t in tasks.data if t.get("status") in ["pending", "in_progress"]])
    
    # Get skill statistics
    skills = supabase.table("skills").select("id").execute()
    total_skills = len(skills.data)
    
    # Get user skills distribution
    user_skills = supabase.table("user_skills").select("skill_id, status").execute()
    
    return {
        "total_users": total_users,
        "total_skills": total_skills,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "total_assignments": len(tasks.data),
        "user_skills_count": len(user_skills.data)
    }


@router.get("/users")
async def get_all_users(limit: int = 50, offset: int = 0):
    """Get all users with pagination"""
    supabase = get_supabase_client()
    users = supabase.table("users").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return {"users": users.data, "total": len(users.data)}


@router.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: str):
    """Get detailed analytics for a user"""
    supabase = get_supabase_client()
    
    # Get user
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get task completion rate
    all_tasks = supabase.table("task_assignments").select("status").eq("user_id", user_id).execute()
    completed = len([t for t in all_tasks.data if t.get("status") == "completed"])
    completion_rate = (completed / len(all_tasks.data) * 100) if all_tasks.data else 0
    
    # Get skills progress
    user_skills = supabase.table("user_skills").select("*, skills(*)").eq("user_id", user_id).execute()
    
    # Get MCQ results
    mcqs = supabase.table("mcq_assessments").select("*").eq("user_id", user_id).execute()
    avg_mcq_score = sum([m.get("percentage_score", 0) for m in mcqs.data]) / len(mcqs.data) if mcqs.data else 0
    
    return {
        "user": user.data[0],
        "task_completion_rate": round(completion_rate, 2),
        "total_tasks": len(all_tasks.data),
        "completed_tasks": completed,
        "skills_progress": user_skills.data,
        "average_mcq_score": round(avg_mcq_score, 2),
        "total_mcq_assessments": len(mcqs.data)
    }


# Skills Management
@router.post("/skills", response_model=dict)
async def create_skill(skill: SkillCreate):
    """Create a new skill"""
    supabase = get_supabase_client()
    result = supabase.table("skills").insert(skill.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create skill")
    return result.data[0]


@router.get("/skills")
async def get_all_skills():
    """Get all skills"""
    supabase = get_supabase_client()
    skills = supabase.table("skills").select("*").order("name").execute()
    return {"skills": skills.data}


# Tasks Management
@router.post("/tasks", response_model=dict)
async def create_task(task: TaskCreate):
    """Create a new task"""
    supabase = get_supabase_client()
    result = supabase.table("tasks").insert(task.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return result.data[0]


@router.get("/tasks")
async def get_all_tasks(skill_id: Optional[str] = None):
    """Get all tasks"""
    supabase = get_supabase_client()
    query = supabase.table("tasks").select("*, skills(*)")
    if skill_id:
        query = query.eq("skill_id", skill_id)
    tasks = query.order("order_index").execute()
    return {"tasks": tasks.data}


# Handouts Management
@router.post("/handouts", response_model=dict)
async def create_handout(handout: HandoutCreate):
    """Create a new handout"""
    supabase = get_supabase_client()
    result = supabase.table("handouts").insert(handout.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create handout")
    return result.data[0]


@router.get("/handouts")
async def get_all_handouts(skill_id: Optional[str] = None):
    """Get all handouts"""
    supabase = get_supabase_client()
    query = supabase.table("handouts").select("*, skills(*)")
    if skill_id:
        query = query.eq("skill_id", skill_id)
    handouts = query.order("order_index").execute()
    return {"handouts": handouts.data}


# MCQ Management
@router.post("/mcqs", response_model=dict)
async def create_mcq(mcq: MCQCreate):
    """Create a new MCQ"""
    supabase = get_supabase_client()
    result = supabase.table("mcqs").insert(mcq.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create MCQ")
    return result.data[0]


# Notification Management
@router.get("/notifications/settings/{user_id}")
async def get_notification_settings(user_id: str):
    """Get notification settings for a user"""
    supabase = get_supabase_client()
    settings = supabase.table("notification_settings").select("*").eq("user_id", user_id).execute()
    if not settings.data:
        # Create default settings
        supabase.table("notification_settings").insert({"user_id": user_id}).execute()
        settings = supabase.table("notification_settings").select("*").eq("user_id", user_id).execute()
    return settings.data[0] if settings.data else {}


@router.put("/notifications/settings/{user_id}")
async def update_notification_settings(user_id: str, settings: NotificationSettingsUpdate):
    """Update notification settings"""
    supabase = get_supabase_client()
    result = supabase.table("notification_settings").update(settings.dict(exclude_unset=True)).eq("user_id", user_id).execute()
    return result.data[0] if result.data else {}


@router.post("/notifications/test/{user_id}")
async def send_test_notification(user_id: str, notification_type: str = "task_reminder"):
    """Send a test notification"""
    notification_service = NotificationService()
    
    # Get a task assignment for testing
    supabase = get_supabase_client()
    assignment = supabase.table("task_assignments").select("*").eq("user_id", user_id).limit(1).execute()
    
    if assignment.data:
        await notification_service.send_task_reminder(user_id, assignment.data[0]["id"], "daily")
        return {"message": "Test notification sent"}
    else:
        return {"message": "No tasks found for testing"}


@router.get("/reports/export")
async def export_reports(format: str = "json"):
    """Export analytics reports"""
    supabase = get_supabase_client()
    
    # Get comprehensive data
    users = supabase.table("users").select("*").execute()
    tasks = supabase.table("task_assignments").select("*").execute()
    skills = supabase.table("skills").select("*").execute()
    mcqs = supabase.table("mcq_assessments").select("*").execute()
    
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "users": users.data,
        "tasks": tasks.data,
        "skills": skills.data,
        "mcq_assessments": mcqs.data
    }
    
    return report

