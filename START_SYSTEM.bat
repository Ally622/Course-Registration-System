@echo off
echo ========================================================
echo Course Registration System - Startup Script
echo ========================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Checking MySQL connection...
python -c "from db import get_connection; conn = get_connection(); print('MySQL Connected!'); conn.close()"
if errorlevel 1 (
    echo ERROR: Cannot connect to MySQL database
    echo Please check:
    echo   1. MySQL server is running
    echo   2. Database 'course_registration_system' exists
    echo   3. Credentials in config.py are correct
    pause
    exit /b 1
)
echo.

echo Starting Flask development server...
echo.
echo ========================================================
echo System will start at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo ========================================================
echo.

python app.py
pause
