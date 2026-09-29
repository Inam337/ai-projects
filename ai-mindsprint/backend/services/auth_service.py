"""
Authentication Service
Handles user registration, login, and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import get_supabase_client, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
import uuid

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.access_token_expire_minutes = JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Dictionary containing user data (e.g., {"sub": user_id, "email": email})
            expires_delta: Optional expiration time delta
        
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Optional[Dict]:
        """
        Decode and verify a JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def register_user(self, email: str, password: str, full_name: str = None, phone_number: str = None) -> Dict:
        """
        Register a new user
        
        Args:
            email: User email
            password: Plain text password
            full_name: Optional full name
            phone_number: Optional phone number
        
        Returns:
            Dictionary with user data and access token
        """
        # Check if user already exists
        existing = self.supabase.table("users").select("*").eq("email", email).execute()
        if existing.data:
            raise ValueError("User with this email already exists")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "phone_number": phone_number,
            "role": "learner",
            "current_level": "beginner",
            "total_points": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "is_active": True,
            "email_verified": False
        }
        
        result = self.supabase.table("users").insert(user_data).execute()
        if not result.data:
            raise ValueError("Failed to create user")
        
        user = result.data[0]
        
        # Create notification settings
        self.supabase.table("notification_settings").insert({
            "user_id": user_id
        }).execute()
        
        # Create access token
        access_token = self.create_access_token(
            data={"sub": user_id, "email": email, "role": user.get("role", "learner")}
        )
        
        # Remove password hash from response
        user.pop("password_hash", None)
        
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user and return token
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            Dictionary with user data and access token, or None if authentication fails
        """
        # Get user from database
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        
        if not result.data:
            return None
        
        user = result.data[0]
        
        # Verify password
        if not self.verify_password(password, user.get("password_hash", "")):
            return None
        
        # Check if user is active
        if not user.get("is_active", True):
            raise ValueError("User account is inactive")
        
        # Update last login
        self.supabase.table("users").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        # Create access token
        access_token = self.create_access_token(
            data={"sub": user["id"], "email": email, "role": user.get("role", "learner")}
        )
        
        # Remove password hash from response
        user.pop("password_hash", None)
        
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        """
        Get current user from JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            User data dictionary or None if token is invalid
        """
        payload = self.decode_access_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        # Get user from database
        result = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            return None
        
        user = result.data[0]
        user.pop("password_hash", None)
        return user
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
        
        Returns:
            True if successful, False otherwise
        """
        # Get user
        result = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            return False
        
        user = result.data[0]
        
        # Verify old password
        if not self.verify_password(old_password, user.get("password_hash", "")):
            return False
        
        # Hash new password
        new_password_hash = self.hash_password(new_password)
        
        # Update password
        self.supabase.table("users").update({
            "password_hash": new_password_hash,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
        
        return True
    
    def reset_password_request(self, email: str) -> bool:
        """
        Request password reset (sends email with reset token)
        
        Args:
            email: User email
        
        Returns:
            True if email exists, False otherwise
        """
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        if not result.data:
            return False
        
        # In production, send email with reset token
        # For now, just return True
        return True

