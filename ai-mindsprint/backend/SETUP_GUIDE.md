# Setup Guide - Skill-Based LMS

## Quick Start

### Step 1: Database Setup

1. Go to your Supabase project: https://supabase.com/dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the entire content from `database/schema.sql`
4. Click **Run** to create all tables
5. (Optional) Run seed data:
   ```bash
   python database/seed_data.py
   ```

### Step 2: Environment Configuration

Create/update `.env` file in `backend/` directory:

```env
SUPABASE_URL=https://wepldvbcodphtvmhsgxw.supabase.co
SUPABASE_KEY=your_actual_api_key_here

# Optional: Email (SendGrid or SMTP)
SENDGRID_API_KEY=your_key
# OR
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional: WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Roadmap
USE_MOCK_ROADMAP=true
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run the Server

```bash
uvicorn main:app --reload
```

Server will start at: http://localhost:8000

## Testing the API

### 1. Test Connection
```bash
curl http://localhost:8000/api/test
```

### 2. Register a User
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "phone_number": "+1234567890",
    "selected_skills": ["backend", "frontend"]
  }'
```

### 3. Get User Dashboard
```bash
curl http://localhost:8000/api/users/{user_id}/dashboard
```

### 4. View API Documentation
Visit: http://localhost:8000/docs

## Database Tables Created

The schema creates these tables:
- ✅ users
- ✅ skills
- ✅ user_skills
- ✅ roadmaps
- ✅ tasks
- ✅ task_assignments
- ✅ handouts
- ✅ handout_deliveries
- ✅ mcqs
- ✅ mcq_assessments
- ✅ badges
- ✅ user_badges
- ✅ notifications
- ✅ notification_settings
- ✅ certificates
- ✅ activity_logs

## Key Features Implemented

✅ **Skill Selection & Roadmaps**
- User selects skills during registration
- System fetches roadmaps (mock or roadmap.sh)
- Converts roadmaps to tasks automatically

✅ **Task Assignment Engine**
- Auto-assigns initial tasks based on user level
- Assigns next tasks after completion
- Priority queue management

✅ **Notifications**
- Email notifications
- WhatsApp notifications (via Twilio)
- Daily, 1-day, 1-hour, overdue reminders
- Configurable notification settings

✅ **Handouts**
- Auto-delivery when tasks assigned
- Support for PDFs, URLs, videos, GitHub repos
- Sent via email and WhatsApp

✅ **MCQ System**
- Auto-generate 20-question assessments
- Automatic evaluation
- Score calculation and points

✅ **Rewards & Gamification**
- Badge system
- Points tracking
- Streak tracking
- Level promotions (beginner → intermediate → advanced → expert)

✅ **Admin Portal**
- User analytics
- Task management
- Skill management
- Handout management
- MCQ management
- Notification settings
- Report export

## API Endpoints Summary

### User APIs
- `POST /api/users/register` - Register with skills
- `GET /api/users/{id}` - Get user
- `GET /api/users/{id}/dashboard` - Dashboard data

### Task APIs
- `GET /api/tasks/assignments/{user_id}` - Get assignments
- `POST /api/tasks/assignments/{id}/complete` - Complete task
- `GET /api/tasks/assignments/{id}/handouts` - Get handouts

### MCQ APIs
- `POST /api/mcqs/assessments/generate` - Generate assessment
- `POST /api/mcqs/assessments/{id}/submit` - Submit answers

### Rewards APIs
- `GET /api/rewards/{user_id}/summary` - Rewards summary
- `GET /api/rewards/{user_id}/badges` - User badges

### Admin APIs
- `GET /api/admin/dashboard` - Admin stats
- `POST /api/admin/skills` - Create skill
- `POST /api/admin/tasks` - Create task
- `POST /api/admin/handouts` - Create handout
- `POST /api/admin/mcqs` - Create MCQ

## Next Steps

1. **Configure Notifications**: Add email/WhatsApp credentials for full functionality
2. **Add More MCQs**: Use admin API to add more questions
3. **Create Handouts**: Upload study materials via admin API
4. **Customize Badges**: Add more badges via admin API
5. **Integrate Frontend**: Connect your frontend to these APIs

## Troubleshooting

**Import Errors**: Make sure you're running from the `backend/` directory

**Database Errors**: Verify tables were created in Supabase SQL Editor

**Connection Errors**: Check SUPABASE_URL and SUPABASE_KEY in `.env`

**Notification Errors**: Notifications will work in mock mode if credentials not set

