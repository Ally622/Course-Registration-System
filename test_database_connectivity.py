"""
Database Connectivity Test Script
Run this to verify database connection and data presence
"""

import mysql.connector
from config import Config

def test_connection():
    """Test basic database connection"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        print("✅ Database connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        return None

def test_tables(connection):
    """Check if all required tables exist"""
    required_tables = [
        'users', 'students', 'admins', 'lecturers', 'schools', 'departments',
        'programmes', 'courses', 'semesters', 'registrations', 'timetable',
        'results', 'kcse_info', 'kcse_grades', 'applications', 'announcements',
        'notifications', 'password_reset_tokens', 'logs'
    ]
    
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    existing_tables = [table[0] for table in cursor.fetchall()]
    
    print("\n📋 Table Check:")
    for table in required_tables:
        if table in existing_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} records")
        else:
            print(f"  ❌ {table}: MISSING")
    
    cursor.close()

def test_critical_data(connection):
    """Check if critical data exists"""
    cursor = connection.cursor(dictionary=True)
    
    print("\n🔍 Critical Data Check:")
    
    # Check schools
    cursor.execute("SELECT COUNT(*) as count FROM schools")
    schools_count = cursor.fetchone()['count']
    print(f"  Schools: {schools_count} {'✅' if schools_count > 0 else '❌ NONE'}")
    
    # Check programmes
    cursor.execute("SELECT COUNT(*) as count FROM programmes")
    programmes_count = cursor.fetchone()['count']
    print(f"  Programmes: {programmes_count} {'✅' if programmes_count > 0 else '❌ NONE'}")
    
    # Check courses
    cursor.execute("SELECT COUNT(*) as count FROM courses")
    courses_count = cursor.fetchone()['count']
    print(f"  Courses: {courses_count} {'✅' if courses_count > 0 else '❌ NONE'}")
    
    # Check programme-course link
    cursor.execute("SELECT COUNT(*) as count FROM courses WHERE programme_id IS NOT NULL")
    linked_courses = cursor.fetchone()['count']
    print(f"  Courses linked to programmes: {linked_courses} {'✅' if linked_courses > 0 else '❌ NONE'}")
    
    # Check active semester
    cursor.execute("SELECT COUNT(*) as count FROM semesters WHERE is_active = 1")
    active_semesters = cursor.fetchone()['count']
    print(f"  Active semesters: {active_semesters} {'✅' if active_semesters > 0 else '❌ NONE'}")
    
    # Check admin user
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()['count']
    print(f"  Admin users: {admin_count} {'✅' if admin_count > 0 else '❌ NONE'}")
    
    cursor.close()

def test_programme_structure(connection):
    """Check programme-course relationships"""
    cursor = connection.cursor(dictionary=True)
    
    print("\n📚 Programme Structure:")
    cursor.execute("""
        SELECT p.programme_name, p.programme_prefix, COUNT(c.course_id) as course_count
        FROM programmes p
        LEFT JOIN courses c ON p.programme_id = c.programme_id 
            AND c.year_of_study = 1 AND c.semester = 1
        GROUP BY p.programme_id
        ORDER BY p.programme_name
    """)
    
    programmes = cursor.fetchall()
    for prog in programmes:
        status = '✅' if prog['course_count'] >= 6 else '⚠️'
        print(f"  {status} {prog['programme_prefix']}: {prog['course_count']} courses (Year 1 Sem 1)")
    
    cursor.close()

if __name__ == "__main__":
    print("="*60)
    print("DATABASE CONNECTIVITY TEST")
    print("="*60)
    
    connection = test_connection()
    if connection:
        try:
            test_tables(connection)
            test_critical_data(connection)
            test_programme_structure(connection)
            
            print("\n" + "="*60)
            print("✅ TEST COMPLETE")
            print("="*60)
        finally:
            connection.close()
    else:
        print("\n❌ Cannot proceed - database connection failed")
        print("\nTroubleshooting:")
        print("1. Start XAMPP MySQL")
        print("2. Verify database 'course_registration' exists")
        print("3. Check config.py credentials")
