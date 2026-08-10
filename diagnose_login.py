"""
Login Diagnostic Script
Run this to diagnose the login issue.
"""
import sys
sys.path.insert(0, r'c:\Users\CHEMOGET\Desktop\3.1\software engineering\COURSE_REGISTRATION_SYSTEM\Course_Registration')

from config import Config

print("=== DATABASE CONFIG ===")
print(f"DB_HOST:     {Config.DB_HOST}")
print(f"DB_USER:     {Config.DB_USER}")
print(f"DB_PASSWORD: {repr(Config.DB_PASSWORD)}")
print(f"DB_NAME:     {Config.DB_NAME}")
print(f"DB_PORT:     {Config.DB_PORT}")
print()

try:
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT DATABASE() as db")
    row = cursor.fetchone()
    print(f"Connected database: {row['db']}")
    print()

    # Show all users
    cursor.execute("SELECT user_id, email, role, is_active, LEFT(password_hash,35) as hash_preview FROM users")
    users = cursor.fetchall()
    print(f"=== USERS TABLE ({len(users)} rows) ===")
    for u in users:
        print(f"  ID={u['user_id']} | {u['email']} | role={u['role']} | active={u['is_active']} | hash={u['hash_preview']}...")
    print()

    # Show all students
    cursor.execute("SELECT student_id, user_id, student_name, registration_number FROM students")
    students = cursor.fetchall()
    print(f"=== STUDENTS TABLE ({len(students)} rows) ===")
    for s in students:
        print(f"  student_id={s['student_id']} | user_id={s['user_id']} | name={s['student_name']} | reg_num={s['registration_number']}")
    print()

    # Full password_hash for first student user
    cursor.execute("""
        SELECT u.user_id, u.email, u.password_hash, u.role
        FROM users u
        INNER JOIN students s ON u.user_id = s.user_id
        LIMIT 5
    """)
    student_users = cursor.fetchall()
    print("=== STUDENT USER PASSWORD HASHES (full) ===")
    for su in student_users:
        print(f"  ID={su['user_id']} | {su['email']} | role={su['role']}")
        print(f"    hash={su['password_hash']}")
    print()

    # Test bcrypt verification
    try:
        from flask_bcrypt import Bcrypt
        bcp = Bcrypt()

        test_passwords = ["admin123", "student123", "lecturer123", "password", "password123"]
        print("=== PASSWORD VERIFICATION TEST ===")
        for su in student_users[:2]:
            print(f"\n  Testing user: {su['email']}")
            for pw in test_passwords:
                try:
                    result = bcp.check_password_hash(su['password_hash'], pw)
                    if result:
                        print(f"    ✓ MATCH: password = '{pw}'")
                    else:
                        print(f"    ✗ No match: '{pw}'")
                except Exception as e:
                    print(f"    ! Error testing '{pw}': {e}")
    except ImportError:
        print("flask_bcrypt not installed — cannot test password verification")

    cursor.close()
    conn.close()
    print("\nDiagnostic complete.")

except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
