# Skill-Based Learning Management System (LMS) Backend

A comprehensive Learning Management System built with FastAPI and Supabase, featuring personalized learning paths, automated task assignments, progress tracking, and gamification.

## 🚀 Features

- **JWT Authentication**: Secure user authentication with JWT tokens and bcrypt password hashing
- **User Registration & Login**: Complete signup and login functionality
- **Skill Selection & Roadmap Integration**: Integrates with roadmap.sh (or mock data) to generate personalized learning paths
- **Task Assignment Engine**: Automatically assigns tasks based on user level and progress
- **Smart Notifications**: Email and WhatsApp reminders (daily, 1-day, 1-hour, overdue)
- **Study Material Delivery**: Automated handout delivery via email and WhatsApp
- **MCQ Assessments**: Auto-generate and evaluate 20-question assessments
- **Rewards & Gamification**: Badges, points, streaks, and level promotions
- **Admin Portal**: Comprehensive admin dashboard with analytics and management tools

## 📋 Prerequisites

- Python 3.11+
- Supabase account and project
- (Optional) Twilio account for WhatsApp notifications
- (Optional) SendGrid account for email notifications

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://wepldvbcodphtvmhsgxw.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDGRID_API_KEY=your_sendgrid_key

# WhatsApp Configuration (Optional - Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Roadmap Configuration
USE_MOCK_ROADMAP=true  # Set to false to try roadmap.sh API

# JWT Authentication Configuration
JWT_SECRET_KEY=2e988d3ea1457c644652ef2ae70cad5b
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days (optional)
```

### 3. Initialize Database

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the SQL script from `database/schema.sql` to create all tables
4. If you have an existing users table, run `database/migration_add_auth.sql` to add auth fields
5. (Optional) Run `python database/seed_data.py` to seed initial data

### 4. Run the Application

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python app.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Authentication Endpoints
- `POST /api/auth/signup` - Register a new user with password
- `POST /api/auth/login` - Login with email/password (OAuth2 form)
- `POST /api/auth/login/json` - Login with JSON body
- `GET /api/auth/me` - Get current authenticated user
- `POST /api/auth/change-password` - Change user password
- `POST /api/auth/verify-token` - Verify JWT token validity

### User Endpoints
- `GET /api/users/{user_id}` - Get user details
- `GET /api/users/{user_id}/skills` - Get user's skills
- `GET /api/users/{user_id}/dashboard` - Get user dashboard

### Task Endpoints
- `GET /api/tasks/assignments/{user_id}` - Get all task assignments
- `GET /api/tasks/assignments/{user_id}/pending` - Get pending tasks
- `GET /api/tasks/assignments/{user_id}/overdue` - Get overdue tasks
- `POST /api/tasks/assignments/{assignment_id}/start` - Start a task
- `POST /api/tasks/assignments/{assignment_id}/complete` - Complete a task
- `GET /api/tasks/assignments/{assignment_id}/handouts` - Get task handouts

### MCQ Endpoints
- `POST /api/mcqs/assessments/generate` - Generate new assessment
- `POST /api/mcqs/assessments/{assessment_id}/submit` - Submit assessment
- `GET /api/mcqs/assessments/{assessment_id}` - Get assessment results
- `GET /api/mcqs/assessments/{user_id}/history` - Get assessment history

### Rewards Endpoints
- `GET /api/rewards/{user_id}/summary` - Get rewards summary
- `GET /api/rewards/{user_id}/badges` - Get user badges
- `GET /api/rewards/{user_id}/streak` - Get streak information
- `POST /api/rewards/{user_id}/update-streak` - Update daily streak

### Admin Endpoints
- `GET /api/admin/dashboard` - Admin dashboard statistics
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/{user_id}/analytics` - User analytics
- `POST /api/admin/skills` - Create skill
- `POST /api/admin/tasks` - Create task
- `POST /api/admin/handouts` - Create handout
- `POST /api/admin/mcqs` - Create MCQ
- `GET /api/admin/reports/export` - Export reports

## 🗄️ Database Schema

The database includes the following main tables:

- **users** - User profiles and progress
- **skills** - Available skills to learn
- **user_skills** - User-skill relationships
- **roadmaps** - Learning roadmaps from roadmap.sh
- **tasks** - Learning tasks and challenges
- **task_assignments** - User task assignments
- **handouts** - Study materials
- **mcqs** - Multiple choice questions
- **mcq_assessments** - User assessments
- **badges** - Available badges
- **user_badges** - User badge achievements
- **notifications** - Notification history
- **certificates** - User certificates
- **activity_logs** - User activity tracking

See `database/schema.sql` for complete schema.

## 🔄 Workflow

1. **User Registration**: User selects skills they want to learn
2. **Roadmap Generation**: System fetches roadmap from roadmap.sh (or uses mock)
3. **Task Creation**: Roadmap milestones are converted to tasks
4. **Task Assignment**: Initial tasks are automatically assigned
5. **Notifications**: Reminders sent via email/WhatsApp
6. **Handout Delivery**: Study materials sent when tasks are assigned
7. **Task Completion**: User completes tasks and earns points
8. **Next Tasks**: System automatically assigns next tasks
9. **Badge Awards**: System checks and awards badges
10. **Level Promotion**: User promoted based on points
11. **MCQ Assessment**: After duration, system generates MCQs
12. **Evaluation**: MCQs automatically evaluated and points awarded

## 🧪 Testing

Test the connection:
```bash
python test_connection.py
```

Test endpoints using the Swagger UI at `/docs` or use tools like Postman/curl.

## 📝 Notes

- **Authentication**: Uses JWT tokens with bcrypt password hashing
- **Password Security**: Passwords are never stored in plain text
- **Token Expiration**: JWT tokens expire after 7 days by default
- The system uses mock roadmap data by default (set `USE_MOCK_ROADMAP=true`)
- Email/WhatsApp notifications will work if credentials are configured
- All endpoints return JSON responses
- Protected endpoints require `Authorization: Bearer <token>` header

## 🔐 Authentication

See `AUTH_GUIDE.md` for detailed authentication documentation including:
- How to sign up and login
- How to use JWT tokens
- How to protect your routes
- Testing authentication

## 🐛 Troubleshooting

### Database Connection Issues
- Verify SUPABASE_URL and SUPABASE_KEY in `.env`
- Check Supabase project is active
- Run `python test_connection.py` to test

### Dependency Issues
- Run `reinstall_deps.bat` (Windows) or `reinstall_deps.sh` (Linux/Mac)
- Or manually: `pip uninstall -y supabase gotrue postgrest storage3 realtime httpx && pip install -r requirements.txt`

### Notification Issues
- Check email/WhatsApp credentials in `.env`
- Notifications will log to console if credentials not configured

## 📄 License

This project is part of the AI Mindsprint Learning Management System.
