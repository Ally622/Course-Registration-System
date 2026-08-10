"""
Test what password matches the seed hash.
Uses ASCII only output to avoid encoding issues.
"""
from flask_bcrypt import Bcrypt
b = Bcrypt()

# The exact hash from seed_data.sql
h = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W'

print(f"Hash length: {len(h)}")
print(f"Hash: {h}")
print()

passwords = ['admin123', 'student123', 'lecturer123', 'password', 'password123', 'Admin123', '123456', 'test123', 'university', 'uni123']
print("Testing passwords against seed hash:")
for pw in passwords:
    try:
        result = b.check_password_hash(h, pw)
        mark = "MATCH" if result else "no match"
        print(f"  '{pw}': {mark}")
    except Exception as e:
        print(f"  '{pw}': ERROR - {str(e)[:50]}")

print()
print("NEW HASHES (for setup_complete.sql):")
passwords_to_hash = {
    'admin123': 'Admin and staff',
    'student123': 'Students',
}
for pw, label in passwords_to_hash.items():
    new_hash = b.generate_password_hash(pw).decode('utf-8')
    verify = b.check_password_hash(new_hash, pw)
    print(f"  {label} password='{pw}'")
    print(f"    hash: {new_hash}")
    print(f"    verify: {'PASS' if verify else 'FAIL'}")
