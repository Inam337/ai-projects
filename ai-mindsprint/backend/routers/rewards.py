"""
Rewards and Gamification API endpoints
"""
from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rewards_service import RewardsService
from config import get_supabase_client

router = APIRouter(prefix="/api/rewards", tags=["rewards"])


@router.get("/{user_id}/summary")
async def get_rewards_summary(user_id: str):
    """Get comprehensive rewards summary"""
    rewards_service = RewardsService()
    summary = await rewards_service.get_user_rewards_summary(user_id)
    return summary


@router.get("/{user_id}/badges")
async def get_user_badges(user_id: str):
    """Get all badges earned by user"""
    supabase = get_supabase_client()
    badges = supabase.table("user_badges").select("*, badges(*)").eq("user_id", user_id).order("earned_at", desc=True).execute()
    return {"badges": [b.get("badges", {}) for b in badges.data]}


@router.get("/{user_id}/streak")
async def get_user_streak(user_id: str):
    """Get user streak information"""
    supabase = get_supabase_client()
    user = supabase.table("users").select("current_streak, longest_streak, last_activity_date").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    return user.data[0]


@router.post("/{user_id}/update-streak")
async def update_streak(user_id: str):
    """Update user's daily streak"""
    rewards_service = RewardsService()
    streak_info = await rewards_service.update_streak(user_id)
    return streak_info


@router.get("/badges/all")
async def get_all_badges():
    """Get all available badges"""
    supabase = get_supabase_client()
    badges = supabase.table("badges").select("*").eq("is_active", True).execute()
    return {"badges": badges.data}


@router.get("/{user_id}/certificates")
async def get_user_certificates(user_id: str):
    """Get all certificates earned by user"""
    supabase = get_supabase_client()
    certificates = supabase.table("certificates").select("*, skills(*)").eq("user_id", user_id).order("issued_at", desc=True).execute()
    return {"certificates": certificates.data}

