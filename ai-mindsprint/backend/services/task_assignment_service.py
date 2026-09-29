"""
Task Assignment Engine
Automatically assigns tasks based on user's skill level and progress
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import get_supabase_client
import uuid


class TaskAssignmentService:
    """Service to automatically assign tasks to users"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def assign_initial_tasks(self, user_id: str, skill_id: str) -> List[Dict]:
        """
        Assign initial tasks when user selects a skill
        
        Args:
            user_id: UUID of the user
            skill_id: UUID of the skill
        
        Returns:
            List of assigned task IDs
        """
        # Get user's current level
        user_data = self.supabase.table("users").select("current_level").eq("id", user_id).execute()
        user_level = user_data.data[0]["current_level"] if user_data.data else "beginner"
        
        # Get tasks for this skill, filtered by difficulty
        tasks = self.supabase.table("tasks").select("*").eq("skill_id", skill_id).eq("is_active", True).execute()
        
        # Filter tasks by user level
        level_mapping = {
            "beginner": ["beginner"],
            "intermediate": ["beginner", "intermediate"],
            "advanced": ["beginner", "intermediate", "advanced"],
            "expert": ["beginner", "intermediate", "advanced"]
        }
        
        allowed_difficulties = level_mapping.get(user_level, ["beginner"])
        filtered_tasks = [t for t in tasks.data if t.get("difficulty") in allowed_difficulties]
        
        # Sort by order_index and take first 5 tasks
        filtered_tasks.sort(key=lambda x: x.get("order_index", 0))
        initial_tasks = filtered_tasks[:5]
        
        # Assign tasks
        assignments = []
        for task in initial_tasks:
            due_date = datetime.utcnow() + timedelta(days=7)  # 7 days from now
            
            assignment = {
                "user_id": user_id,
                "task_id": task["id"],
                "assigned_at": datetime.utcnow().isoformat(),
                "due_date": due_date.isoformat(),
                "status": "pending",
                "priority": 5,
                "auto_assigned": True
            }
            
            result = self.supabase.table("task_assignments").insert(assignment).execute()
            if result.data:
                assignments.append(result.data[0])
        
        return assignments
    
    async def assign_next_tasks(self, user_id: str, skill_id: str, completed_task_id: str) -> List[Dict]:
        """
        Assign next tasks after user completes a task
        
        Args:
            user_id: UUID of the user
            skill_id: UUID of the skill
            completed_task_id: UUID of the completed task
        
        Returns:
            List of newly assigned tasks
        """
        # Get completed task
        completed_task = self.supabase.table("tasks").select("*").eq("id", completed_task_id).execute()
        if not completed_task.data:
            return []
        
        task = completed_task.data[0]
        milestone_num = task.get("milestone_number", 0)
        order_index = task.get("order_index", 0)
        
        # Find next tasks in sequence
        next_tasks = self.supabase.table("tasks").select("*").eq("skill_id", skill_id).eq("is_active", True).gt("order_index", order_index).order("order_index").limit(3).execute()
        
        assignments = []
        for next_task in next_tasks.data:
            # Check if already assigned
            existing = self.supabase.table("task_assignments").select("*").eq("user_id", user_id).eq("task_id", next_task["id"]).execute()
            if existing.data:
                continue
            
            # Check prerequisites
            prerequisites = next_task.get("prerequisites", [])
            if prerequisites:
                # Check if all prerequisites are completed
                prereq_completed = await self._check_prerequisites(user_id, prerequisites)
                if not prereq_completed:
                    continue
            
            # Assign task
            due_date = datetime.utcnow() + timedelta(days=7)
            assignment = {
                "user_id": user_id,
                "task_id": next_task["id"],
                "assigned_at": datetime.utcnow().isoformat(),
                "due_date": due_date.isoformat(),
                "status": "pending",
                "priority": 5,
                "auto_assigned": True
            }
            
            result = self.supabase.table("task_assignments").insert(assignment).execute()
            if result.data:
                assignments.append(result.data[0])
        
        return assignments
    
    async def _check_prerequisites(self, user_id: str, prerequisites: List) -> bool:
        """Check if all prerequisite tasks are completed"""
        if not prerequisites:
            return True
        
        # Get all user's completed tasks for this skill
        # This is a simplified check - in production, you'd want more robust logic
        return True  # Simplified for now
    
    async def update_task_priority(self, user_id: str, task_assignment_id: str, priority: int):
        """Update task priority"""
        self.supabase.table("task_assignments").update({"priority": priority}).eq("id", task_assignment_id).eq("user_id", user_id).execute()
    
    async def mark_task_completed(self, user_id: str, task_assignment_id: str, submission_data: Optional[Dict] = None) -> Dict:
        """
        Mark a task as completed and award points
        
        Args:
            user_id: UUID of the user
            task_assignment_id: UUID of the task assignment
            submission_data: Optional submission data (code, links, etc.)
        
        Returns:
            Updated task assignment
        """
        # Get task assignment
        assignment = self.supabase.table("task_assignments").select("*, tasks(*)").eq("id", task_assignment_id).eq("user_id", user_id).execute()
        if not assignment.data:
            raise ValueError("Task assignment not found")
        
        task_data = assignment.data[0]
        task = task_data.get("tasks", {})
        points = task.get("points_reward", 10)
        
        # Update assignment
        update_data = {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "points_earned": points
        }
        if submission_data:
            update_data["submission_data"] = submission_data
        
        result = self.supabase.table("task_assignments").update(update_data).eq("id", task_assignment_id).execute()
        
        # Update user points
        user = self.supabase.table("users").select("total_points").eq("id", user_id).execute()
        current_points = user.data[0]["total_points"] if user.data else 0
        self.supabase.table("users").update({"total_points": current_points + points}).eq("id", user_id).execute()
        
        # Log activity
        self.supabase.table("activity_logs").insert({
            "user_id": user_id,
            "activity_type": "task_completed",
            "entity_type": "task",
            "entity_id": task_assignment_id,
            "description": f"Completed task: {task.get('title', '')}",
            "points_earned": points
        }).execute()
        
        return result.data[0] if result.data else {}

