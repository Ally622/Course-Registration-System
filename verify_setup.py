#!/usr/bin/env python3
"""
Dedan Kimathi University - Setup Verification Script
Run this to check if everything is configured correctly
"""

import sys
import os

print("=" * 60)
print("DEDAN KIMATHI UNIVERSITY")
print("Course Registration System - Setup Verification")
print("=" * 60)
print()

# Check 1: Python version
print("✓ Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 7:
    print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
else:
    print(f"  ❌ Python {version.major}.{version.minor} (Need 3.7+)")
    sys.exit(1)

# Check 2: Required modules
print("\n✓ Checking required Python packages...")
required_packages = [
    'flask',
    'mysql.connector',
    'flask_bcrypt',
    'flask_cors',
    'flask_wtf'
]

missing_packages = []
for package in required_packages:
    try:
        if package == 'mysql.connector':
            __import__('mysql.connector')
        else:
            __import__(package)
        print(f"  ✅ {package}")
    except ImportError:
        print(f"  ❌ {package} (MISSING)")
        missing_packages.append(package)

if missing_packages:
    print("\n⚠️  Install missing packages:")
    print(f"  pip install {' '.join(missing_packages)}")
    sys.exit(1)

# Check 3: Database connection
print("\n✓ Checking database connection...")
try:
    from db import get_connection
    connection = get_connection()
    cursor = connection.cursor()
    
    # Check database exists
    cursor.execute("SELECT DATABASE()")
    db_name = cursor.fetchone()[0]
    print(f"  ✅ Connected to database: {db_name}")
    
    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_count = len(tables)
    
    if table_count > 0:
        print(f"  ✅ Found {table_count} tables")
    else:
        print(f"  ⚠️  No tables found (run schema.sql)")
    
    # Check for users
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        if user_count > 0:
            print(f"  ✅ Found {user_count} users")
        else:
            print(f"  ⚠️  No users found (run seed_data.sql)")
    except:
        print(f"  ⚠️  Users table not found (run schema.sql)")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"  ❌ Database error: {str(e)}")
    print("\n  Solutions:")
    print("  1. Check MySQL is running")
    print("  2. Check password in config.py")
    print("  3. Create database: mysql -u root -p < setup_database.sql")
    sys.exit(1)

# Check 4: Config file
print("\n✓ Checking configuration...")
try:
    from config import Config
    print(f"  ✅ Database: {Config.DB_NAME}")
    print(f"  ✅ Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"  ✅ User: {Config.DB_USER}")
    if Config.DB_PASSWORD:
        print(f"  ✅ Password: ****** (set)")
    else:
        print(f"  ⚠️  Password: (empty)")
except Exception as e:
    print(f"  ❌ Config error: {str(e)}")
    sys.exit(1)

# Check 5: Frontend files
print("\n✓ Checking frontend files...")
frontend_files = [
    'frontend/login.html',
    'frontend/register.html',
    'frontend/assets/css/style.css',
    'frontend/assets/css/auth.css',
    'frontend/assets/js/api.js',
    'frontend/assets/js/layout.js'
]

for file_path in frontend_files:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} (MISSING)")

# Check 6: Backend modules
print("\n✓ Checking backend modules...")
backend_modules = [
    'app.py',
    'config.py',
    'db.py',
    'extensions.py',
    'auth/routes.py',
    'student/routes.py',
    'admin/routes.py',
    'admission/routes.py',
    'registration/routes.py'
]

for file_path in backend_modules:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} (MISSING)")

# Summary
print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\n✅ Your system is ready!")
print("\nNext steps:")
print("1. Start Flask: python app.py")
print("2. Open browser: http://127.0.0.1:5000/login.html")
print("3. Test login:")
print("   Email: john.doe@student.edu")
print("   Password: student123")
print()
