"""Check admin password and reset if needed."""
from app import create_app
from extensions import bcrypt
from db import get_connection

app = create_app()
with app.app_context():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    # Get admin hash
    cur.execute("SELECT user_id, email, role, password_hash FROM users WHERE role='admin' LIMIT 1")
    admin = cur.fetchone()
    print(f"Admin: {admin['email']}")
    
    # Test password
    try:
        ok = bcrypt.check_password_hash(admin['password_hash'], 'admin123')
        print(f"Password 'admin123' matches: {ok}")
    except Exception as e:
        print(f"Hash check error: {e}")
        ok = False
    
    if not ok:
        print("Resetting admin password to 'admin123'...")
        new_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        cur.execute("UPDATE users SET password_hash = %s WHERE role IN ('admin', 'registrar')", (new_hash,))
        conn.commit()
        print(f"New hash: {new_hash[:30]}...")
        
        # Verify
        cur.execute("SELECT password_hash FROM users WHERE role='admin' LIMIT 1")
        row = cur.fetchone()
        ok2 = bcrypt.check_password_hash(row['password_hash'], 'admin123')
        print(f"Re-verified: {ok2}")
    else:
        print("Password is correct — no reset needed.")
    
    # Also reset student password for safety
    cur.execute("SELECT user_id, password_hash FROM users WHERE role='student' LIMIT 1")
    stu = cur.fetchone()
    if stu:
        try:
            stu_ok = bcrypt.check_password_hash(stu['password_hash'], 'student123')
            print(f"\nStudent 'student123' matches: {stu_ok}")
        except:
            print("Student hash error — resetting...")
            new_hash = bcrypt.generate_password_hash('student123').decode('utf-8')
            cur.execute("UPDATE users SET password_hash=%s WHERE role='student'", (new_hash,))
            conn.commit()
            print("Student password reset to 'student123'")
    
    cur.close()
    conn.close()
print("Done.")
