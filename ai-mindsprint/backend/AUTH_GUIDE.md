# Authentication Guide

## JWT Authentication Implementation

The system uses JWT (JSON Web Tokens) for authentication with secure password hashing using bcrypt.

## Setup

### 1. Environment Variables

Add to your `.env` file:

```env
JWT_SECRET_KEY=2e988d3ea1457c644652ef2ae70cad5b
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days (optional, defaults to 7 days)
```

### 2. Database Migration

The users table has been updated to include:
- `password_hash` - Bcrypt hashed password
- `email_verified` - Email verification status
- `last_login` - Last login timestamp

Run the updated schema in Supabase SQL Editor.

## API Endpoints

### Sign Up

**POST** `/api/auth/signup`

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "selected_skills": ["backend", "frontend"]
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "learner",
    "current_level": "beginner",
    ...
  }
}
```

### Login

**POST** `/api/auth/login` (Form data - OAuth2 compatible)

Form data:
- `username`: user@example.com (email)
- `password`: securepassword123

**OR**

**POST** `/api/auth/login/json` (JSON body)

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    ...
  }
}
```

### Get Current User

**GET** `/api/auth/me`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  ...
}
```

### Change Password

**POST** `/api/auth/change-password`

Headers:
```
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

### Verify Token

**POST** `/api/auth/verify-token`

Headers:
```
Authorization: Bearer <access_token>
```

## Using Authentication in Your Routes

### Option 1: Using Dependency Injection

```python
from routers.auth import get_current_user, get_current_active_user

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user['email']}"}
```

### Option 2: Manual Token Validation

```python
from services.auth_service import AuthService

@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    auth_service = AuthService()
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user": user}
```

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Secure token-based authentication
3. **Token Expiration**: Tokens expire after 7 days (configurable)
4. **Password Verification**: Secure password comparison
5. **Account Status Check**: Inactive accounts cannot login

## Testing Authentication

### Using cURL

**Sign Up:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Swagger UI

1. Visit http://localhost:8000/docs
2. Use the `/api/auth/signup` or `/api/auth/login` endpoints
3. Copy the `access_token` from the response
4. Click the "Authorize" button at the top
5. Enter: `Bearer <your_access_token>`
6. Now all protected endpoints will use this token

## Password Requirements

Currently, there are no password complexity requirements enforced. You can add validation in the `UserSignup` model if needed:

```python
from pydantic import validator

class UserSignup(BaseModel):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Add more validation as needed
        return v
```

## Token Structure

JWT tokens contain:
- `sub`: User ID
- `email`: User email
- `role`: User role (learner/admin)
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

## Error Responses

- **401 Unauthorized**: Invalid credentials or expired token
- **400 Bad Request**: Invalid input data
- **500 Internal Server Error**: Server error

## Next Steps

1. Implement email verification
2. Add password reset functionality
3. Implement refresh tokens
4. Add rate limiting for login attempts
5. Add password complexity requirements

