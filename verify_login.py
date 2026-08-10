"""
Quick verification script - checks DB, passwords, and Flask startup.
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("STEP 1: Database & Password Verification")
print("=" * 60)

try:
    from flask_bcrypt import Bcrypt
    from db import get_connection
    b = Bcrypt()
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Check student passwords
    cur.execute("SELECT u.email, u.password_hash, u.role, s.registration_number FROM users u LEFT JOIN students s ON u.user_id=s.user_id WHERE u.role='student' LIMIT 3")
    rows = cur.fetchall()
    print("\nStudent accounts:")
    for r in rows:
        pw_student = b.check_password_hash(r['password_hash'], 'student123')
        print(f"  email={r['email']}")
        print(f"  reg_number={r['registration_number']}")
        print(f"  password 'student123': {'PASS' if pw_student else 'FAIL'}")
        print()

    # Check admin/staff passwords
    cur.execute("SELECT email, password_hash, role FROM users WHERE role != 'student'")
    rows = cur.fetchall()
    print("Staff accounts:")
    for r in rows:
        pw_admin = b.check_password_hash(r['password_hash'], 'admin123')
        print(f"  email={r['email']} | role={r['role']} | password 'admin123': {'PASS' if pw_admin else 'FAIL'}")

    cur.close()
    conn.close()
    print("\nDB check PASSED.")
except Exception as e:
    import traceback
    print(f"DB check FAILED: {e}")
    traceback.print_exc()

print()
print("=" * 60)
print("STEP 2: Flask App Import Check")
print("=" * 60)

try:
    from app import create_app
    app = create_app()
    print("Flask app created: PASS")
    
    # List all routes
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"  {','.join(rule.methods - {'HEAD','OPTIONS'})} {rule.rule}")
        
        auth_routes = [r for r in routes if '/auth/' in r]
        student_routes = [r for r in routes if '/student/' in r]
        print(f"\nAuth routes ({len(auth_routes)}):")
        for r in auth_routes:
            print(r)
        print(f"\nStudent routes ({len(student_routes)}):")
        for r in student_routes[:10]:
            print(r)
        print(f"\nTotal routes: {len(routes)}")
except Exception as e:
    import traceback
    print(f"Flask import FAILED: {e}")
    traceback.print_exc()

print()
print("=" * 60)
print("STEP 3: Test Login Flow (in-process)")
print("=" * 60)

try:
    import json
    with app.test_client() as client:
        # Test student login via email (no reg number)
        resp = client.post('/auth/login',
            data=json.dumps({'identifier': 'john.doe@student.edu', 'password': 'student123'}),
            content_type='application/json')
        data = resp.get_json()
        print(f"Login with email (john.doe@student.edu / student123):")
        print(f"  Status: {resp.status_code}")
        print(f"  Success: {data.get('success')}")
        print(f"  Message: {data.get('message')}")
        if data.get('success'):
            u = data.get('user', {})
            print(f"  User: {u.get('name')} | role={u.get('role')} | reg={u.get('registration_number')}")

        print()

        # Test login with registration number
        resp2 = client.post('/auth/login',
            data=json.dumps({'identifier': 'CS/2026/0001', 'password': 'student123'}),
            content_type='application/json')
        data2 = resp2.get_json()
        print(f"Login with reg number (CS/2026/0001 / student123):")
        print(f"  Status: {resp2.status_code}")
        print(f"  Success: {data2.get('success')}")
        print(f"  Message: {data2.get('message')}")

        print()

        # Test admin login
        resp3 = client.post('/auth/login',
            data=json.dumps({'identifier': 'admin@university.edu', 'password': 'admin123'}),
            content_type='application/json')
        data3 = resp3.get_json()
        print(f"Admin login (admin@university.edu / admin123):")
        print(f"  Status: {resp3.status_code}")
        print(f"  Success: {data3.get('success')}")
        print(f"  Message: {data3.get('message')}")

        print()

        # Test invalid credentials
        resp4 = client.post('/auth/login',
            data=json.dumps({'identifier': 'john.doe@student.edu', 'password': 'wrongpassword'}),
            content_type='application/json')
        data4 = resp4.get_json()
        print(f"Invalid credentials test:")
        print(f"  Status: {resp4.status_code}")
        print(f"  Success: {data4.get('success')} (expected False)")
        print(f"  Message: {data4.get('message')}")

except Exception as e:
    import traceback
    print(f"Login test FAILED: {e}")
    traceback.print_exc()
