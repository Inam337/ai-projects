#!/bin/bash
echo "Uninstalling old Supabase packages..."
pip uninstall -y supabase gotrue postgrest storage3 realtime httpx

echo ""
echo "Installing updated dependencies..."
pip install -r requirements.txt

echo ""
echo "Done! Please make sure your .env file has SUPABASE_KEY set."

