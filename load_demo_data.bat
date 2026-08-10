@echo off
echo ========================================
echo LOADING DEMO DATA INTO DATABASE
echo ========================================
echo.

echo This script will load comprehensive demo data into your database.
echo.
echo Demo Data Includes:
echo   - 2 Admin accounts (admin@university.edu / admin123)
echo   - 3 Student accounts (john.doe@student.edu / student123)
echo   - 2 Lecturer accounts
echo   - 5 Schools with multiple departments
echo   - 12 Programmes (CS, IT, SE, Engineering, Business, etc.)
echo   - 100+ Course units across all programmes
echo   - Sample registrations and results
echo   - Academic calendar (2026/2027 session)
echo.

set /p proceed="Do you want to proceed? (y/n): "
if /i not "%proceed%"=="y" (
    echo Operation cancelled.
    pause
    exit /b
)

echo.
echo Connecting to MySQL...
echo.

REM Prompt for MySQL password
set /p mysql_password="Enter MySQL root password (press Enter if no password): "

echo.
echo Loading schema first...
if "%mysql_password%"=="" (
    mysql -u root course_registration_system < database\schema.sql
) else (
    mysql -u root -p%mysql_password% course_registration_system < database\schema.sql
)

if errorlevel 1 (
    echo.
    echo ERROR: Failed to load schema!
    echo Make sure:
    echo   1. MySQL is running
    echo   2. Database 'course_registration_system' exists
    echo   3. Your password is correct
    pause
    exit /b 1
)

echo.
echo Loading demo data...
if "%mysql_password%"=="" (
    mysql -u root course_registration_system < database\seed_data.sql
) else (
    mysql -u root -p%mysql_password% course_registration_system < database\seed_data.sql
)

if errorlevel 1 (
    echo.
    echo ERROR: Failed to load demo data!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Demo data loaded successfully!
echo ========================================
echo.
echo Test Accounts:
echo.
echo ADMIN:
echo   Email: admin@university.edu
echo   Password: admin123
echo.
echo STUDENT:
echo   Email: john.doe@student.edu
echo   OR Student ID: CS/2026/0001
echo   Password: student123
echo.
echo LECTURER:
echo   Email: dr.johnson@university.edu
echo   Password: lecturer123
echo.
echo ========================================
echo You can now start the system:
echo   python app.py
echo ========================================
echo.
pause
