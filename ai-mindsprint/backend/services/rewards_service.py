"""
Rewards and Gamification Service
Handles badges, points, streaks, and level promotions
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import get_supabase_client


class RewardsService:
    """Service to manage rewards, badges, and gamification"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def check_and_award_badges(self, user_id: str, skill_id: Optional[str] = None) -> List[Dict]:
        """
        Check if user qualifies for any badges and award them
        
        Args:
            user_id: UUID of the user
            skill_id: Optional skill ID to check skill-specific badges
        
        Returns:
            List of newly awarded badges
        """
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            return []
        
        user_data = user.data[0]
        newly_awarded = []
        
        # Get all active badges
        badges_query = self.supabase.table("badges").select("*").eq("is_active", True)
        if skill_id:
            badges_query = badges_query.eq("skill_id", skill_id)
        
        badges = badges_query.execute()
        
        # Get user's existing badges
        user_badges = self.supabase.table("user_badges").select("badge_id").eq("user_id", user_id).execute()
        existing_badge_ids = [b["badge_id"] for b in user_badges.data]
        
        for badge in badges.data:
            badge_id = badge["id"]
            
            # Skip if already awarded
            if badge_id in existing_badge_ids:
                continue
            
            # Check if user qualifies
            if await self._check_badge_eligibility(user_id, badge, user_data):
                # Award badge
                self.supabase.table("user_badges").insert({
                    "user_id": user_id,
                    "badge_id": badge_id,
                    "earned_at": datetime.utcnow().isoformat()
                }).execute()
                
                newly_awarded.append(badge)
                
                # Send notification
                from services.notification_service import NotificationService
                notification_service = NotificationService()
                await notification_service.send_badge_notification(user_id, badge_id)
        
        return newly_awarded
    
    async def _check_badge_eligibility(self, user_id: str, badge: Dict, user_data: Dict) -> bool:
        """Check if user is eligible for a badge"""
        badge_type = badge.get("badge_type")
        criteria = badge.get("criteria", {})
        points_required = badge.get("points_required", 0)
        
        # Check points requirement
        if points_required > 0 and user_data.get("total_points", 0) < points_required:
            return False
        
        if badge_type == "streak":
            streak_days = criteria.get("days", 7)
            return user_data.get("current_streak", 0) >= streak_days
        
        elif badge_type == "skill_completion":
            skill_id = badge.get("skill_id")
            if not skill_id:
                return False
            
            user_skill = self.supabase.table("user_skills").select("*").eq("user_id", user_id).eq("skill_id", skill_id).execute()
            if not user_skill.data:
                return False
            
            return user_skill.data[0].get("progress_percentage", 0) >= 100
        
        elif badge_type == "milestone":
            milestone_num = criteria.get("milestone_number")
            skill_id = badge.get("skill_id")
            if not milestone_num or not skill_id:
                return False
            
            # Check if user completed this milestone
            completed_tasks = self.supabase.table("task_assignments").select("*, tasks(*)").eq("user_id", user_id).eq("status", "completed").execute()
            for task in completed_tasks.data:
                task_data = task.get("tasks", {})
                if task_data.get("skill_id") == skill_id and task_data.get("milestone_number") == milestone_num:
                    return True
            
            return False
        
        elif badge_type == "points":
            return user_data.get("total_points", 0) >= points_required
        
        return False
    
    async def update_streak(self, user_id: str) -> Dict:
        """
        Update user's daily streak
        
        Args:
            user_id: UUID of the user
        
        Returns:
            Updated streak information
        """
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            return {}
        
        user_data = user.data[0]
        last_activity = user_data.get("last_activity_date")
        current_streak = user_data.get("current_streak", 0)
        longest_streak = user_data.get("longest_streak", 0)
        
        today = datetime.utcnow().date()
        
        if last_activity:
            last_date = datetime.fromisoformat(str(last_activity)).date() if isinstance(last_activity, str) else last_activity
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Already updated today
                return {"current_streak": current_streak, "longest_streak": longest_streak}
            elif days_diff == 1:
                # Consecutive day
                new_streak = current_streak + 1
            else:
                # Streak broken
                new_streak = 1
        else:
            # First activity
            new_streak = 1
        
        # Update longest streak if needed
        if new_streak > longest_streak:
            longest_streak = new_streak
        
        # Update user
        self.supabase.table("users").update({
            "current_streak": new_streak,
            "longest_streak": longest_streak,
            "last_activity_date": today.isoformat()
        }).eq("id", user_id).execute()
        
        # Check for streak badges
        await self.check_and_award_badges(user_id)
        
        return {
            "current_streak": new_streak,
            "longest_streak": longest_streak
        }
    
    async def check_level_promotion(self, user_id: str) -> Optional[Dict]:
        """
        Check if user should be promoted to next level
        
        Args:
            user_id: UUID of the user
        
        Returns:
            Promotion information if promoted, None otherwise
        """
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            return None
        
        user_data = user.data[0]
        current_level = user_data.get("current_level", "beginner")
        total_points = user_data.get("total_points", 0)
        
        # Level progression thresholds
        level_thresholds = {
            "beginner": 100,
            "intermediate": 500,
            "advanced": 1500,
            "expert": 5000
        }
        
        level_order = ["beginner", "intermediate", "advanced", "expert"]
        current_index = level_order.index(current_level) if current_level in level_order else 0
        
        # Check if should promote
        if current_index < len(level_order) - 1:
            next_level = level_order[current_index + 1]
            threshold = level_thresholds.get(next_level, 0)
            
            if total_points >= threshold:
                # Promote user
                self.supabase.table("users").update({
                    "current_level": next_level
                }).eq("id", user_id).execute()
                
                # Log activity
                self.supabase.table("activity_logs").insert({
                    "user_id": user_id,
                    "activity_type": "level_up",
                    "entity_type": "user",
                    "entity_id": user_id,
                    "description": f"Promoted to {next_level} level"
                }).execute()
                
                # Send notification
                from services.notification_service import NotificationService
                notification_service = NotificationService()
                await notification_service.send_email(
                    user_data.get("email"),
                    f"Level Up! You're now {next_level.title()}",
                    f"Congratulations! You've been promoted to {next_level} level!"
                )
                
                return {
                    "old_level": current_level,
                    "new_level": next_level,
                    "points": total_points
                }
        
        return None
    
    async def get_user_rewards_summary(self, user_id: str) -> Dict:
        """Get comprehensive rewards summary for user"""
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        user_badges = self.supabase.table("user_badges").select("*, badges(*)").eq("user_id", user_id).execute()
        certificates = self.supabase.table("certificates").select("*").eq("user_id", user_id).execute()
        
        return {
            "user": user.data[0] if user.data else {},
            "badges": [b.get("badges", {}) for b in user_badges.data],
            "certificates": certificates.data,
            "total_badges": len(user_badges.data),
            "total_certificates": len(certificates.data)
        }

