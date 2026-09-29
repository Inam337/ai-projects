"""
Main entry point for the FastAPI application
"""
from app import app
from config import get_supabase_client

# Test Supabase connection on startup
try:
    supabase = get_supabase_client()
    print("✓ Supabase database connected successfully")
    print(f"✓ Supabase URL: https://wepldvbcodphtvmhsgxw.supabase.co")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Supabase client: {e}")
    print("⚠ The application will start, but database features may not work.")

# This allows uvicorn to find the app when running: uvicorn main:app
__all__ = ["app"]

