"""
Quick Authentication Test Script
Tests password verification without running the full Flask app
"""

from flask_bcrypt import Bcrypt
import mysql.connector
from config import DevelopmentConfig

bcrypt = Bcrypt()

def test_auth():
    """Test authentication against database"""
    
    # Connect to database
    conn = mysql.connector.connect(
        host=DevelopmentConfig.DB_HOST,
        user=DevelopmentConfig.DB_USER,
        password=DevelopmentConfig.DB_PASSWORD,
        database=DevelopmentConfig.DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    
    print("\n" + "="*70)
    print("QUICK AUTHENTICATION TEST")
    print("="*70 + "\n")
    
    # Test credentials from screenshot
    test_credentials = [
        ('admin@univesity.edu', 'admin123'),  # As shown in screenshot
        ('admin@university.edu', 'admin123'), # Correct spelling
        ('registrar@university.edu', 'admin123'),
        ('john.doe@student.edu', 'student123'),
    ]
    
    for email, password in test_credentials:
        print(f"Testing: {email} / {password}")
        
        cursor.execute("SELECT user_id, email, password_hash, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"  ❌ User NOT FOUND in database!\n")
            continue
        
        print(f"  ✓ User exists: {user['email']} (Role: {user['role']})")
        print(f"  ✓ Hash in DB: {user['password_hash'][:40]}...")
        
        # Test the password
        try:
            if bcrypt.check_password_hash(user['password_hash'], password):
                print(f"  ✅ PASSWORD CORRECT! Login should work.\n")
            else:
                print(f"  ❌ PASSWORD WRONG! Hash doesn't match.\n")
        except Exception as e:
            print(f"  ❌ ERROR checking password: {e}\n")
    
    cursor.close()
    conn.close()
    
    print("="*70)
    print("\nIf passwords don't match, run:")
    print("  python fix_authentication.py")
    print("  Select option 5 (Fix everything)")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_auth()
