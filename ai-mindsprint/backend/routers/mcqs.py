"""
MCQ API endpoints
"""
from fastapi import APIRouter, HTTPException
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import MCQAssessmentSubmit, MCQCreate, MCQResponse
from services.mcq_service import MCQService
from typing import List

router = APIRouter(prefix="/api/mcqs", tags=["mcqs"])


@router.post("/assessments/generate")
async def generate_assessment(user_id: str, skill_id: str, assessment_type: str = "skill_evaluation", num_questions: int = 20):
    """Generate a new MCQ assessment"""
    mcq_service = MCQService()
    assessment = await mcq_service.generate_assessment(user_id, skill_id, assessment_type, num_questions)
    
    if not assessment:
        raise HTTPException(status_code=500, detail="Failed to generate assessment")
    
    return assessment


@router.post("/assessments/{assessment_id}/submit")
async def submit_assessment(assessment_id: str, user_id: str, submission: MCQAssessmentSubmit):
    """Submit and evaluate an assessment"""
    mcq_service = MCQService()
    result = await mcq_service.submit_assessment(assessment_id, user_id, submission.answers, submission.time_taken_seconds)
    return result


@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str, user_id: str):
    """Get assessment details and results"""
    mcq_service = MCQService()
    assessment = await mcq_service.get_assessment_results(assessment_id, user_id)
    return assessment


@router.get("/assessments/{user_id}/history")
async def get_assessment_history(user_id: str, skill_id: str = None):
    """Get assessment history for a user"""
    from config import get_supabase_client
    supabase = get_supabase_client()
    
    query = supabase.table("mcq_assessments").select("*").eq("user_id", user_id)
    if skill_id:
        query = query.eq("skill_id", skill_id)
    
    assessments = query.order("created_at", desc=True).execute()
    return {"assessments": assessments.data}


# Admin endpoints for MCQ management
@router.post("/", response_model=MCQResponse)
async def create_mcq(mcq: MCQCreate):
    """Create a new MCQ (Admin only)"""
    from config import get_supabase_client
    supabase = get_supabase_client()
    
    mcq_data = mcq.dict()
    result = supabase.table("mcqs").insert(mcq_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create MCQ")
    
    return result.data[0]


@router.get("/skill/{skill_id}", response_model=List[MCQResponse])
async def get_mcqs_by_skill(skill_id: str):
    """Get all MCQs for a skill"""
    from config import get_supabase_client
    supabase = get_supabase_client()
    
    mcqs = supabase.table("mcqs").select("*").eq("skill_id", skill_id).eq("is_active", True).execute()
    return mcqs.data

