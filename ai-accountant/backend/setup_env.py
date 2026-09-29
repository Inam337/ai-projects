#!/usr/bin/env python3
"""
Environment setup script for AI Accountant
This script helps you create the .env file with the required API credentials.
"""

import os

def create_env_file():
    """Create .env file with API credentials."""
    env_content = """# AI Accountant Environment Variables
OPENAI_API_KEY=028fa2e1-fb69-4cca-89aa-1e11ffc4dcc1
OPENAI_BASE_URL=https://openai.dplit.com/v1
OPENAI_MODEL=gpt-4o-mini
"""
    
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"Created .env file at: {env_file_path}")
        print("API credentials have been set up successfully!")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        print("\nManual setup required:")
        print("Create a file named '.env' in the backend directory with:")
        print(env_content)
        return False

def verify_env_setup():
    """Verify that environment variables are properly loaded."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')
        
        if api_key and base_url:
            print(f"Environment variables loaded successfully!")
            print(f"API Key: {api_key[:10]}...")
            print(f"Base URL: {base_url}")
            return True
        else:
            print("Environment variables not found!")
            return False
    except ImportError:
        print("python-dotenv not installed. Run: pip install python-dotenv")
        return False

if __name__ == "__main__":
    print("AI Accountant - Environment Setup")
    print("=" * 40)
    
    # Create .env file
    if create_env_file():
        print("\nVerifying setup...")
        verify_env_setup()
    
    print("\nNext steps:")
    print("1. Start the server: python -m uvicorn main:app --reload")
    print("2. Test the API: http://localhost:8000/docs")
    print("3. Upload a CSV file to test categorization")
