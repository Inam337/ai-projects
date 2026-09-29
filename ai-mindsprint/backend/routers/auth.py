"""
Authentication API endpoints
Login, Signup, and JWT token management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from models.schemas import UserResponse

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Request/Response Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    selected_skills: Optional[list] = []  # List of skill slugs


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current authenticated user"""
    auth_service = AuthService()
    user = auth_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Dependency to get current active user"""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    """
    Register a new user
    
    - **email**: User email address
    - **password**: User password (will be hashed)
    - **full_name**: Optional full name
    - **phone_number**: Optional phone number
    - **selected_skills**: Optional list of skill slugs to learn
    """
    auth_service = AuthService()
    
    try:
        # Register user
        result = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number
        )
        
        # If skills are selected, process them (similar to register endpoint in users.py)
        if user_data.selected_skills:
            from services.roadmap_service import RoadmapService
            from services.task_assignment_service import TaskAssignmentService
            from config import get_supabase_client
            
            supabase = get_supabase_client()
            roadmap_service = RoadmapService()
            task_service = TaskAssignmentService()
            user_id = result["user"]["id"]
            
            for skill_slug in user_data.selected_skills:
                # Get or create skill
                skill = supabase.table("skills").select("*").eq("slug", skill_slug).execute()
                if not skill.data:
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
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and get access token
    
    Use form data with:
    - **username**: User email
    - **password**: User password
    """
    auth_service = AuthService()
    
    # OAuth2PasswordRequestForm uses 'username' field for email
    result = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result


@router.post("/login/json", response_model=TokenResponse)
async def login_json(login_data: UserLogin):
    """
    Login user with JSON body (alternative to form-based login)
    
    - **email**: User email
    - **password**: User password
    """
    auth_service = AuthService()
    
    result = auth_service.authenticate_user(login_data.email, login_data.password)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get current authenticated user information
    Requires valid JWT token in Authorization header
    """
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Change user password
    
    - **old_password**: Current password
    - **new_password**: New password
    """
    auth_service = AuthService()
    
    success = auth_service.change_password(
        current_user["id"],
        password_data.old_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    return {"message": "Password changed successfully"}


@router.post("/reset-password-request")
async def reset_password_request(email: str):
    """
    Request password reset (sends email with reset link)
    
    - **email**: User email address
    """
    auth_service = AuthService()
    
    success = auth_service.reset_password_request(email)
    
    if not success:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verify if a JWT token is valid
    
    Returns user information if token is valid
    """
    auth_service = AuthService()
    user = auth_service.get_current_user(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "valid": True,
        "user": user
    }

