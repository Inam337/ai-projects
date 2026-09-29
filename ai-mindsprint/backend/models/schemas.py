"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


# User Models
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    selected_skills: List[str]  # List of skill slugs


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    phone_number: Optional[str]
    role: str
    current_level: str
    total_points: int
    current_streak: int
    longest_streak: int
    is_active: bool
    created_at: datetime


# Skill Models
class SkillCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    category: str
    icon_url: Optional[str] = None
    roadmap_id: Optional[str] = None
    difficulty_level: str = "beginner"
    estimated_duration_days: Optional[int] = None


class SkillResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    category: str
    icon_url: Optional[str]
    roadmap_id: Optional[str]
    difficulty_level: str
    estimated_duration_days: Optional[int]
    is_active: bool
    created_at: datetime


# Task Models
class TaskCreate(BaseModel):
    skill_id: str
    roadmap_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    task_type: str
    difficulty: str = "beginner"
    estimated_duration_minutes: Optional[int] = None
    points_reward: int = 10
    milestone_number: Optional[int] = None
    prerequisites: Optional[List[str]] = []
    order_index: int = 0


class TaskResponse(BaseModel):
    id: str
    skill_id: str
    roadmap_id: Optional[str]
    title: str
    description: Optional[str]
    task_type: str
    difficulty: str
    estimated_duration_minutes: Optional[int]
    points_reward: int
    milestone_number: Optional[int]
    order_index: int
    is_active: bool
    created_at: datetime


# Task Assignment Models
class TaskAssignmentResponse(BaseModel):
    id: str
    user_id: str
    task_id: str
    assigned_at: datetime
    due_date: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str
    priority: int
    auto_assigned: bool
    points_earned: int
    submission_data: Optional[Dict[str, Any]] = None


class TaskSubmission(BaseModel):
    submission_data: Dict[str, Any]
    notes: Optional[str] = None


# Handout Models
class HandoutCreate(BaseModel):
    task_id: Optional[str] = None
    skill_id: str
    title: str
    description: Optional[str] = None
    handout_type: str = "pdf"
    content_url: str
    order_index: int = 0


class HandoutResponse(BaseModel):
    id: str
    task_id: Optional[str]
    skill_id: str
    title: str
    description: Optional[str]
    handout_type: str
    content_url: str
    file_path: Optional[str]
    order_index: int
    is_active: bool
    created_at: datetime


# MCQ Models
class MCQCreate(BaseModel):
    skill_id: str
    question: str
    options: List[Dict[str, Any]]
    correct_answer_id: int
    explanation: Optional[str] = None
    difficulty: str = "beginner"
    points: int = 1


class MCQResponse(BaseModel):
    id: str
    skill_id: str
    question: str
    options: List[Dict[str, Any]]
    correct_answer_id: int
    explanation: Optional[str]
    difficulty: str
    points: int
    is_active: bool


class MCQAssessmentSubmit(BaseModel):
    answers: Dict[str, int]  # {mcq_id: answer_id}
    time_taken_seconds: int


# Badge Models
class BadgeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    badge_type: str
    icon_url: Optional[str]
    points_required: int


# Notification Models
class NotificationSettingsUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    daily_reminder_enabled: Optional[bool] = None
    daily_reminder_time: Optional[str] = None
    one_day_reminder_enabled: Optional[bool] = None
    one_hour_reminder_enabled: Optional[bool] = None
    overdue_reminder_enabled: Optional[bool] = None

