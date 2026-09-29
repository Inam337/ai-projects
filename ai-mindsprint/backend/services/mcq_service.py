"""
MCQ Generation and Evaluation Service
"""
from typing import List, Dict, Optional
from datetime import datetime
from config import get_supabase_client
import random


class MCQService:
    """Service to generate and evaluate MCQs"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def generate_assessment(self, user_id: str, skill_id: str, assessment_type: str = "skill_evaluation", num_questions: int = 20) -> Dict:
        """
        Generate an MCQ assessment for a user
        
        Args:
            user_id: UUID of the user
            skill_id: UUID of the skill
            assessment_type: Type of assessment ('skill_evaluation', 'milestone', 'periodic')
            num_questions: Number of questions (default 20)
        
        Returns:
            Assessment data
        """
        # Get MCQs for this skill
        mcqs = self.supabase.table("mcqs").select("*").eq("skill_id", skill_id).eq("is_active", True).execute()
        
        if not mcqs.data or len(mcqs.data) < num_questions:
            # If not enough questions, use all available
            question_ids = [q["id"] for q in mcqs.data]
        else:
            # Randomly select questions
            question_ids = random.sample([q["id"] for q in mcqs.data], min(num_questions, len(mcqs.data)))
        
        # Create assessment
        assessment = {
            "user_id": user_id,
            "skill_id": skill_id,
            "assessment_type": assessment_type,
            "total_questions": len(question_ids),
            "questions": question_ids,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat()
        }
        
        result = self.supabase.table("mcq_assessments").insert(assessment).execute()
        
        if result.data:
            # Get full question data for the assessment
            questions_data = []
            for qid in question_ids:
                question = next((q for q in mcqs.data if q["id"] == qid), None)
                if question:
                    questions_data.append({
                        "id": question["id"],
                        "question": question["question"],
                        "options": question["options"],
                        "difficulty": question.get("difficulty", "beginner")
                    })
            
            return {
                "assessment_id": result.data[0]["id"],
                "questions": questions_data,
                "total_questions": len(question_ids)
            }
        
        return {}
    
    async def submit_assessment(self, assessment_id: str, user_id: str, answers: Dict[str, int], time_taken_seconds: int) -> Dict:
        """
        Submit and evaluate an assessment
        
        Args:
            assessment_id: UUID of the assessment
            user_id: UUID of the user
            answers: Dictionary of {mcq_id: answer_id}
            time_taken_seconds: Time taken to complete
        
        Returns:
            Evaluation results
        """
        # Get assessment
        assessment = self.supabase.table("mcq_assessments").select("*").eq("id", assessment_id).eq("user_id", user_id).execute()
        if not assessment.data:
            raise ValueError("Assessment not found")
        
        assessment_data = assessment.data[0]
        question_ids = assessment_data.get("questions", [])
        
        # Get all MCQs
        mcqs = self.supabase.table("mcqs").select("*").in_("id", question_ids).execute()
        mcq_dict = {q["id"]: q for q in mcqs.data}
        
        # Evaluate answers
        correct_count = 0
        total_points = 0
        results = []
        
        for qid in question_ids:
            mcq = mcq_dict.get(qid)
            if not mcq:
                continue
            
            user_answer = answers.get(str(qid))
            correct_answer = mcq.get("correct_answer_id")
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
                points = mcq.get("points", 1)
                total_points += points
            
            results.append({
                "mcq_id": qid,
                "question": mcq.get("question"),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": mcq.get("explanation", "")
            })
        
        # Calculate percentage
        percentage = (correct_count / len(question_ids) * 100) if question_ids else 0
        
        # Update assessment
        update_data = {
            "answers": answers,
            "completed_at": datetime.utcnow().isoformat(),
            "time_taken_seconds": time_taken_seconds,
            "score": correct_count,
            "total_points": total_points,
            "percentage_score": round(percentage, 2),
            "status": "completed"
        }
        
        self.supabase.table("mcq_assessments").update(update_data).eq("id", assessment_id).execute()
        
        # Award points to user
        user = self.supabase.table("users").select("total_points").eq("id", user_id).execute()
        current_points = user.data[0]["total_points"] if user.data else 0
        self.supabase.table("users").update({"total_points": current_points + total_points}).eq("id", user_id).execute()
        
        # Log activity
        self.supabase.table("activity_logs").insert({
            "user_id": user_id,
            "activity_type": "mcq_completed",
            "entity_type": "assessment",
            "entity_id": assessment_id,
            "description": f"Completed MCQ assessment with {correct_count}/{len(question_ids)} correct",
            "points_earned": total_points
        }).execute()
        
        return {
            "assessment_id": assessment_id,
            "score": correct_count,
            "total_questions": len(question_ids),
            "percentage": round(percentage, 2),
            "points_earned": total_points,
            "results": results
        }
    
    async def get_assessment_results(self, assessment_id: str, user_id: str) -> Dict:
        """Get assessment results"""
        assessment = self.supabase.table("mcq_assessments").select("*").eq("id", assessment_id).eq("user_id", user_id).execute()
        if not assessment.data:
            raise ValueError("Assessment not found")
        
        return assessment.data[0]

