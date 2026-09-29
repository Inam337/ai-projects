-- Skill-Based Learning Management System Database Schema
-- Run this in Supabase SQL Editor to create all tables

-- Users table (with JWT authentication)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    role VARCHAR(50) DEFAULT 'learner' CHECK (role IN ('learner', 'admin')),
    current_level VARCHAR(50) DEFAULT 'beginner' CHECK (current_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    total_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skills table
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100), -- e.g., 'Backend', 'Frontend', 'DevOps', 'AI', 'Databases'
    icon_url TEXT,
    roadmap_id VARCHAR(255), -- roadmap.sh roadmap ID
    difficulty_level VARCHAR(50) DEFAULT 'beginner',
    estimated_duration_days INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Skills (Many-to-Many: Users can select multiple skills)
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    current_milestone INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'in_progress' CHECK (status IN ('not_started', 'in_progress', 'completed', 'paused')),
    UNIQUE(user_id, skill_id)
);

-- Roadmaps table (stores roadmap.sh data or custom roadmaps)
CREATE TABLE IF NOT EXISTS roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    roadmap_data JSONB, -- Full roadmap structure from roadmap.sh
    title VARCHAR(255) NOT NULL,
    description TEXT,
    total_milestones INTEGER DEFAULT 0,
    source VARCHAR(50) DEFAULT 'roadmap.sh', -- 'roadmap.sh' or 'custom'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    roadmap_id UUID REFERENCES roadmaps(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN ('daily_challenge', 'weekly_challenge', 'mini_project', 'milestone', 'coding_exercise', 'theory')),
    difficulty VARCHAR(50) DEFAULT 'beginner' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    estimated_duration_minutes INTEGER,
    points_reward INTEGER DEFAULT 10,
    milestone_number INTEGER, -- Which milestone this task belongs to
    prerequisites JSONB, -- Array of task IDs that must be completed first
    order_index INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task Assignments (User-specific task assignments)
CREATE TABLE IF NOT EXISTS task_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'overdue', 'skipped')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    auto_assigned BOOLEAN DEFAULT true,
    points_earned INTEGER DEFAULT 0,
    submission_data JSONB, -- User's submission (code, links, etc.)
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Handouts table
CREATE TABLE IF NOT EXISTS handouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    handout_type VARCHAR(50) DEFAULT 'pdf' CHECK (handout_type IN ('pdf', 'url', 'video', 'github', 'tutorial')),
    content_url TEXT NOT NULL, -- URL to PDF, video, GitHub repo, etc.
    file_path TEXT, -- If uploaded file
    order_index INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Handout Deliveries (Track when handouts are sent to users)
CREATE TABLE IF NOT EXISTS handout_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    handout_id UUID NOT NULL REFERENCES handouts(id) ON DELETE CASCADE,
    task_assignment_id UUID REFERENCES task_assignments(id) ON DELETE SET NULL,
    delivery_method VARCHAR(50) NOT NULL CHECK (delivery_method IN ('email', 'whatsapp', 'both')),
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    opened_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'opened', 'failed'))
);

-- MCQs table
CREATE TABLE IF NOT EXISTS mcqs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    options JSONB NOT NULL, -- Array of option objects: [{"id": 1, "text": "Option A"}, ...]
    correct_answer_id INTEGER NOT NULL,
    explanation TEXT,
    difficulty VARCHAR(50) DEFAULT 'beginner',
    points INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MCQ Assessments (Generated assessments for users)
CREATE TABLE IF NOT EXISTS mcq_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) DEFAULT 'skill_evaluation' CHECK (assessment_type IN ('skill_evaluation', 'milestone', 'periodic')),
    total_questions INTEGER DEFAULT 20,
    questions JSONB NOT NULL, -- Array of MCQ IDs
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    time_taken_seconds INTEGER,
    score INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    percentage_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    answers JSONB, -- User's answers: {"mcq_id": "answer_id", ...}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Badges table
CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    badge_type VARCHAR(50) NOT NULL CHECK (badge_type IN ('skill_completion', 'streak', 'points', 'milestone', 'achievement')),
    icon_url TEXT,
    points_required INTEGER DEFAULT 0,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    criteria JSONB, -- Specific criteria for earning badge
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Badges (Many-to-Many: Users can earn multiple badges)
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_assignment_id UUID REFERENCES task_assignments(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('task_assigned', 'task_reminder', 'task_due_soon', 'task_overdue', 'handout_delivered', 'badge_earned', 'level_up', 'mcq_ready')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    delivery_method VARCHAR(50) DEFAULT 'email' CHECK (delivery_method IN ('email', 'whatsapp', 'both', 'in_app')),
    sent_at TIMESTAMP WITH TIME ZONE,
    scheduled_for TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed')),
    metadata JSONB, -- Additional data for the notification
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification Settings (User preferences for notifications)
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    email_enabled BOOLEAN DEFAULT true,
    whatsapp_enabled BOOLEAN DEFAULT true,
    daily_reminder_enabled BOOLEAN DEFAULT true,
    daily_reminder_time TIME DEFAULT '09:00:00',
    one_day_reminder_enabled BOOLEAN DEFAULT true,
    one_hour_reminder_enabled BOOLEAN DEFAULT true,
    overdue_reminder_enabled BOOLEAN DEFAULT true,
    task_assigned_notification BOOLEAN DEFAULT true,
    badge_notification BOOLEAN DEFAULT true,
    level_up_notification BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Certificates table
CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    certificate_type VARCHAR(50) NOT NULL CHECK (certificate_type IN ('skill_completion', 'milestone', 'level_achievement')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    certificate_url TEXT, -- URL to generated certificate PDF
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activity Log (Track user activities)
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- 'task', 'skill', 'badge', etc.
    entity_id UUID,
    description TEXT,
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_user_id ON task_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_task_id ON task_assignments(task_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);
CREATE INDEX IF NOT EXISTS idx_task_assignments_due_date ON task_assignments(due_date);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled_for ON notifications(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_mcq_assessments_user_id ON mcq_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- Enable Row Level Security (RLS) - Basic policies
-- Note: RLS policies are disabled by default since we're using JWT authentication
-- Application-level authentication will handle access control
-- Uncomment and modify these if you want to enable RLS with custom functions

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE task_assignments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- For RLS with custom JWT auth, you would need to create a function that extracts user_id from JWT
-- Example (commented out):
-- CREATE OR REPLACE FUNCTION get_user_id_from_jwt() RETURNS UUID AS $$
-- BEGIN
--   RETURN current_setting('request.jwt.claim.user_id', true)::UUID;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (id = get_user_id_from_jwt());
-- CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (id = get_user_id_from_jwt());

