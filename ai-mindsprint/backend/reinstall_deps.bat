@echo off
echo ========================================
echo Reinstalling Supabase Dependencies
echo ========================================
echo.
echo Step 1: Uninstalling old packages...
pip uninstall -y supabase gotrue postgrest storage3 realtime httpx

echo.
echo Step 2: Installing updated dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Please make sure your .env file has SUPABASE_KEY set.
echo You can now run: uvicorn main:app --reload
echo.
pause

