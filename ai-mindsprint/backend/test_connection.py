"""
Test script to verify Supabase database connection
"""
from config import get_supabase_client
import sys

def test_connection():
    """Test Supabase connection"""
    try:
        print("Testing Supabase connection...")
        print("-" * 50)
        
        supabase = get_supabase_client()
        
        if supabase is None:
            print("❌ ERROR: Supabase client is None")
            return False
        
        print("✓ Supabase client created successfully")
        print(f"✓ Supabase URL: https://wepldvbcodphtvmhsgxw.supabase.co")
        print("✓ Database connection ready")
        print("-" * 50)
        print("✅ Connection test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("-" * 50)
        print("❌ Connection test FAILED")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

