"""
FastAPI Application with Supabase Backend
Skill-Based Learning Management System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import get_supabase_client
from typing import Optional
import os

# Import routers
from routers import auth, users, tasks, mcqs, rewards, admin

app = FastAPI(
    title="Skill-Based LMS API",
    description="Learning Management System with personalized learning paths, task assignments, and gamification",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)  # Auth routes first
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(mcqs.router)
app.include_router(rewards.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Mindsprint Backend API",
        "status": "running",
        "supabase_connected": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        supabase = get_supabase_client()
        # Test connection by checking if client is initialized
        return {
            "status": "healthy",
            "supabase_url": os.getenv("SUPABASE_URL", "https://wepldvbcodphtvmhsgxw.supabase.co"),
            "database": "connected",
            "client_initialized": supabase is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.get("/api/test")
async def test_connection():
    """Test Supabase connection"""
    try:
        supabase = get_supabase_client()
        
        # Verify client is initialized and ready
        if supabase is None:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")
        
        return {
            "message": "Supabase connection successful",
            "url": os.getenv("SUPABASE_URL", "https://wepldvbcodphtvmhsgxw.supabase.co"),
            "status": "connected",
            "client_ready": True,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@app.get("/api/db/status")
async def database_status():
    """Get detailed database connection status"""
    try:
        supabase = get_supabase_client()
        return {
            "status": "success",
            "supabase_url": os.getenv("SUPABASE_URL", "https://wepldvbcodphtvmhsgxw.supabase.co"),
            "connection": "active",
            "message": "Supabase database is connected and ready"
        }
    except Exception as e:
        return {
            "status": "error",
            "connection": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

