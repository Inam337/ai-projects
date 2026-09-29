"""
Supabase Configuration
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wepldvbcodphtvmhsgxw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlcGxkdmJjb2RwaHR2bWhzZ3h3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM2OTkyNzksImV4cCI6MjA3OTI3NTI3OX0.y1SIo2KljhVyBUCcz9cJMn-OQW_kh92UceRLczaOMJg")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "2e988d3ea1457c644652ef2ae70cad5b")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Lazy initialization - client will be created on first access
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get Supabase client instance (lazy initialization)"""
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_KEY environment variable is required. "
                "Please set it in your .env file or environment variables."
            )
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            error_msg = str(e)
            if "proxy" in error_msg.lower():
                raise ValueError(
                    f"Version compatibility error: {error_msg}\n\n"
                    "Please reinstall dependencies with compatible versions:\n"
                    "pip uninstall -y supabase gotrue postgrest storage3 realtime httpx\n"
                    "pip install -r requirements.txt"
                ) from e
            raise ValueError(
                f"Failed to create Supabase client: {error_msg}. "
                "Please check your SUPABASE_URL and SUPABASE_KEY."
            ) from e
    
    return _supabase_client

