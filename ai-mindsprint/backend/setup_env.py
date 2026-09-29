"""
Helper script to set up environment variables
Run this script to create a .env file with your Supabase credentials
"""
import os

def setup_env():
    """Create .env file with Supabase configuration"""
    supabase_url = "https://wepldvbcodphtvmhsgxw.supabase.co"
    
    print("=" * 50)
    print("Supabase Environment Setup")
    print("=" * 50)
    print(f"\nSupabase URL: {supabase_url}")
    print("\nTo get your Supabase API Key:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings > API")
    print("4. Copy the 'anon' key (for client-side) or 'service_role' key (for server-side)")
    print("\n" + "=" * 50)
    
    api_key = input("\nEnter your Supabase API Key: ").strip()
    
    if not api_key:
        print("Error: API key cannot be empty!")
        return
    
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={api_key}

# Server Configuration
PORT=8000
HOST=0.0.0.0
"""
    
    env_file = ".env"
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"\n✓ Environment file created: {env_file}")
    print("You can now run the application with: python app.py")

if __name__ == "__main__":
    setup_env()

