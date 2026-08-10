"""
Quick database verification script.
Run this to check if your database is properly set up.
"""

from db import get_connection

def verify_database():
    """Check if all required tables exist and have data."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)
        print()
        
        # Check tables
        tables_to_check = [
            'users', 'students', 'admins', 'lecturers',
            'schools', 'departments', 'programmes', 'units',
            'semesters', 'academic_sessions', 'registrations',
            'results', 'timetables', 'system_logs'
        ]
        
        print("Checking tables...")
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            status = "✓" if result['count'] > 0 else "⚠"
            print(f"  {status} {table:25} : {result['count']:5} rows")
        
        print()
        print("-" * 60)
        print()
        
        # Check critical data
        print("Critical Data Checks:")
        print()
        
        # Active users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        active_users = cursor.fetchone()['count']
        print(f"  Active Users: {active_users}")
        
        # Active semester
        cursor.execute("SELECT * FROM semesters WHERE is_active = 1 LIMIT 1")
        active_semester = cursor.fetchone()
        if active_semester:
            print(f"  ✓ Active Semester: {active_semester['semester_name']}")
            print(f"    Registration Open: {active_semester['is_registration_open']}")
            print(f"    Deadline: {active_semester['registration_deadline']}")
        else:
            print("  ⚠ WARNING: No active semester!")
        
        print()
        
        # Active programmes
        cursor.execute("SELECT COUNT(*) as count FROM programmes WHERE is_active = 1")
        active_programmes = cursor.fetchone()['count']
        print(f"  Active Programmes: {active_programmes}")
        
        # Active units
        cursor.execute("SELECT COUNT(*) as count FROM units WHERE is_active = 1")
        active_units = cursor.fetchone()['count']
        print(f"  Active Units/Courses: {active_units}")
        
        print()
        print("=" * 60)
        
        if active_units == 0:
            print()
            print("⚠ WARNING: No active units found!")
            print("Students won't be able to register for courses.")
            print("Run database/seed_data.sql to populate sample data.")
        
        if not active_semester:
            print()
            print("⚠ WARNING: No active semester!")
            print("Registration system requires an active semester.")
            print("Run database/seed_data.sql to create one.")
        
        cursor.close()
        conn.close()
        
        print()
        print("✓ Database verification complete!")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ DATABASE ERROR")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common solutions:")
        print("  1. Make sure MySQL server is running")
        print("  2. Check database name in config.py")
        print("  3. Verify username/password in config.py")
        print("  4. Run database/schema.sql to create tables")
        print()
        return False
    
    return True

if __name__ == "__main__":
    verify_database()
