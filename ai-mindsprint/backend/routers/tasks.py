"""
Task API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import TaskAssignmentResponse, TaskSubmission
from config import get_supabase_client
from services.task_assignment_service import TaskAssignmentService
from services.rewards_service import RewardsService
from services.notification_service import NotificationService
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/assignments/{user_id}", response_model=List[TaskAssignmentResponse])
async def get_user_assignments(user_id: str, status: Optional[str] = None):
    """Get all task assignments for a user"""
    supabase = get_supabase_client()
    
    query = supabase.table("task_assignments").select("*, tasks(*)").eq("user_id", user_id)
    if status:
        query = query.eq("status", status)
    
    assignments = query.order("due_date").execute()
    return assignments.data


@router.get("/assignments/{user_id}/pending")
async def get_pending_tasks(user_id: str):
    """Get pending tasks for a user"""
    supabase = get_supabase_client()
    tasks = supabase.table("task_assignments").select("*, tasks(*)").eq("user_id", user_id).in_("status", ["pending", "in_progress"]).order("priority", desc=True).order("due_date").execute()
    return {"tasks": tasks.data}


@router.get("/assignments/{user_id}/overdue")
async def get_overdue_tasks(user_id: str):
    """Get overdue tasks for a user"""
    supabase = get_supabase_client()
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    tasks = supabase.table("task_assignments").select("*, tasks(*)").eq("user_id", user_id).lt("due_date", now).in_("status", ["pending", "in_progress"]).execute()
    
    # Update status to overdue
    for task in tasks.data:
        supabase.table("task_assignments").update({"status": "overdue"}).eq("id", task["id"]).execute()
    
    return {"tasks": tasks.data}


@router.post("/assignments/{assignment_id}/start")
async def start_task(assignment_id: str, user_id: str):
    """Start a task"""
    supabase = get_supabase_client()
    result = supabase.table("task_assignments").update({
        "status": "in_progress",
        "started_at": datetime.utcnow().isoformat()
    }).eq("id", assignment_id).eq("user_id", user_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    
    # Update streak
    rewards_service = RewardsService()
    await rewards_service.update_streak(user_id)
    
    return result.data[0]


@router.post("/assignments/{assignment_id}/complete")
async def complete_task(assignment_id: str, user_id: str, submission: TaskSubmission):
    """Complete a task and submit work"""
    task_service = TaskAssignmentService()
    rewards_service = RewardsService()
    
    # Mark task as completed
    result = await task_service.mark_task_completed(user_id, assignment_id, submission.submission_data)
    
    # Get task to find skill
    supabase = get_supabase_client()
    assignment = supabase.table("task_assignments").select("*, tasks(*)").eq("id", assignment_id).execute()
    if assignment.data:
        task = assignment.data[0].get("tasks", {})
        skill_id = task.get("skill_id")
        
        # Assign next tasks
        if skill_id:
            await task_service.assign_next_tasks(user_id, skill_id, assignment_id)
        
        # Check for badges and level up
        await rewards_service.check_and_award_badges(user_id, skill_id)
        await rewards_service.check_level_promotion(user_id)
    
    # Update streak
    await rewards_service.update_streak(user_id)
    
    return result


@router.put("/assignments/{assignment_id}/priority")
async def update_task_priority(assignment_id: str, user_id: str, priority: int):
    """Update task priority (1-10)"""
    if priority < 1 or priority > 10:
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 10")
    
    task_service = TaskAssignmentService()
    await task_service.update_task_priority(user_id, assignment_id, priority)
    
    return {"message": "Priority updated successfully"}


@router.get("/assignments/{assignment_id}/handouts")
async def get_task_handouts(assignment_id: str, user_id: str):
    """Get handouts for a task"""
    supabase = get_supabase_client()
    
    # Verify assignment belongs to user
    assignment = supabase.table("task_assignments").select("*, tasks(*)").eq("id", assignment_id).eq("user_id", user_id).execute()
    if not assignment.data:
        raise HTTPException(status_code=404, detail="Task assignment not found")
    
    task = assignment.data[0].get("tasks", {})
    task_id = task.get("id")
    skill_id = task.get("skill_id")
    
    # Get handouts
    handouts = supabase.table("handouts").select("*").eq("task_id", task_id).eq("is_active", True).order("order_index").execute()
    
    # Also get skill-level handouts
    skill_handouts = supabase.table("handouts").select("*").eq("skill_id", skill_id).is_("task_id", "null").eq("is_active", True).order("order_index").execute()
    
    all_handouts = handouts.data + skill_handouts.data
    
    # Send handouts via notification
    notification_service = NotificationService()
    for handout in all_handouts:
        await notification_service.send_handout_notification(user_id, handout["id"], assignment_id)
    
    return {"handouts": all_handouts}

