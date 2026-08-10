# Authentication Issue - Complete Fix Guide

## 🔴 Problem Summary
You're getting "Invalid credentials" error when logging in with `admin@univesity.edu / admin123`, even though these credentials appear correct.

## 🔍 Root Causes Identified

### **Issue #1: Database Logs Table Mismatch** ⚠️ CRITICAL
**Problem:** The authentication code tries to write to a table called `logs`, but the database schema defines it as `system_logs`.

**Location:** `auth/routes.py` line ~576
```python
# WRONG:
INSERT INTO logs (user_id, action, table_name, record_id, new_value)

# CORRECT:
INSERT INTO system_logs (user_id, action, table_name, record_id, description)
```

**Impact:** Every login attempt crashes during the logging step, causing the transaction to rollback and login to fail.

**Status:** ✅ FIXED in the code

---

### **Issue #2: Column Name Mismatch**
**Problem:** Code uses `new_value` but schema might have `description`.

**Status:** ✅ FIXED in the code

---

### **Issue #3: Typo in Email Address** ⚠️
**Problem:** Screenshot shows `admin@univesity.edu` (missing 'r')
But seed data has `admin@university.edu` (correct spelling)

**Impact:** User literally doesn't exist in database!

---

### **Issue #4: Password Hash Compatibility**
**Problem:** Seed data has bcrypt hashes, but if:
- Database charset is wrong
- Bcrypt library version differs
- Hash was corrupted

Then verification will always fail.

---

## ✅ Solution Steps

### **Step 1: Run Quick Test** (2 minutes)
```bash
cd "C:\Users\CHEMOGET\Desktop\3.1\software engineering\COURSE_REGISTRATION_SYSTEM\Course_Registration"
python test_auth_quick.py
```

This will:
- Check if users exist in database
- Test password verification
- Show which credentials work

---

### **Step 2: Run Complete Fix** (5 minutes) ⭐ RECOMMENDED
```bash
python fix_authentication.py
```

Select option **5** (Fix everything)

This will:
1. ✅ Fix the logs table name issue
2. ✅ Reset ALL passwords to fresh hashes
3. ✅ Verify database structure
4. ✅ Show all user accounts

---

### **Step 3: Verify Flask Server** (1 minute)
```bash
python app.py
```

Check Flask logs for any errors during startup.

---

### **Step 4: Test Login** (1 minute)

Open browser to: http://127.0.0.1:5000/login.html

**Test Admin Login:**
- Email: `admin@university.edu` (note correct spelling!)
- Password: `admin123`

**Test Student Login:**
- Email: `john.doe@student.edu`
- Password: `student123`

OR

- Registration Number: `CS/2026/0001`
- Password: `student123`

---

## 🎯 Quick Fixes Without Running Scripts

### Fix #1: Correct the Email Typo
**In the login form, use:**
```
admin@university.edu    (with 'r')
NOT
admin@univesity.edu     (missing 'r')
```

### Fix #2: Check Flask Terminal for Errors
When you click Login, check the Flask terminal. You should see:
```
INFO: Student X requesting programmes list
```

If you see errors like:
```
ERROR: Table 'logs' doesn't exist
```

Then the logs table fix is critical.

---

## 🔧 Manual Database Fix (if scripts don't work)

### Connect to MySQL:
```bash
mysql -u root -p course_registration_system
```

### Check if logs table exists:
```sql
SHOW TABLES LIKE 'logs';
SHOW TABLES LIKE 'system_logs';
```

### If 'logs' exists but 'system_logs' doesn't:
```sql
RENAME TABLE logs TO system_logs;
```

### If 'system_logs' exists, verify columns:
```sql
DESCRIBE system_logs;
```

### If 'new_value' column exists instead of 'description':
```sql
ALTER TABLE system_logs CHANGE new_value description TEXT;
```

### Reset Admin Password Manually:
```sql
-- Generate hash using Python:
-- python -c "from flask_bcrypt import Bcrypt; b=Bcrypt(); print(b.generate_password_hash('admin123').decode())"

-- Then update:
UPDATE users 
SET password_hash = '$2b$12$...[your generated hash]...'
WHERE email = 'admin@university.edu';
```

---

## 📋 Verification Checklist

After running fixes, verify:

- [ ] Flask server starts without errors
- [ ] No "Table 'logs' doesn't exist" errors in Flask logs
- [ ] Login form accepts credentials
- [ ] Successful login redirects to dashboard
- [ ] Browser console shows no errors (F12)
- [ ] Flask terminal shows login success message

---

## 🔍 Debugging Tips

### Check Database Connection
```bash
python test_database_connectivity.py
```

### Check Flask Logs
Watch the terminal where Flask is running. You should see:
```
POST /auth/login
INFO: Admin System Administrator logged in
```

### Check Browser Console (F12)
Should see:
```
[Programmes] Fetching from /admission/programmes...
[Programmes] Response status: 200 OK
```

NOT:
```
Error: Invalid credentials
```

### Check Database Directly
```sql
-- Check users exist
SELECT email, role FROM users;

-- Check password hash
SELECT email, SUBSTRING(password_hash, 1, 20) as hash_preview 
FROM users 
WHERE email = 'admin@university.edu';

-- Check logs table
SHOW TABLES LIKE '%logs%';
```

---

## 🚨 Common Mistakes

1. **Using wrong email spelling:** `univesity` vs `university`
2. **Case sensitivity:** MySQL on Windows is not case-sensitive by default, but Linux is
3. **Copy-paste errors:** Password might have invisible characters
4. **Wrong database:** Make sure you're connected to `course_registration_system`
5. **Old seed data:** If you ran seed_data.sql multiple times, there might be duplicates

---

## 📊 Expected Behavior After Fix

### Successful Login Flow:

1. User enters credentials
2. Frontend sends POST to `/auth/login`
3. Backend finds user in database
4. Backend verifies password hash
5. Backend creates session
6. Backend logs the action to `system_logs` table ✅
7. Backend returns success with user data
8. Frontend redirects to dashboard

### Current Broken Flow:

1. User enters credentials
2. Frontend sends POST to `/auth/login`
3. Backend finds user
4. Backend verifies password ✅
5. Backend tries to log to `logs` table ❌ TABLE DOESN'T EXIST
6. Database throws error
7. Transaction rolls back
8. Login fails with "Invalid credentials"

---

## 💡 Prevention

To prevent this in the future:

1. **Run schema first, then seed data**
   ```bash
   mysql -u root -p course_registration_system < database/schema.sql
   mysql -u root -p course_registration_system < database/seed_data.sql
   ```

2. **Use migrations properly**
   Run all migration files in order

3. **Test authentication immediately after setup**
   ```bash
   python test_auth_quick.py
   ```

4. **Enable detailed logging**
   In `config.py`, set:
   ```python
   DEBUG = True
   SQLALCHEMY_ECHO = True  # If using SQLAlchemy
   ```

---

## 📞 Support

If the issue persists after following this guide:

1. Run diagnostic:
   ```bash
   python fix_authentication.py
   # Choose option 1
   ```

2. Copy the output

3. Check Flask terminal for the exact error message

4. Check browser console (F12) for frontend errors

5. Share:
   - Diagnostic output
   - Flask error logs
   - Browser console errors

---

## ✅ Summary

**Most Likely Cause:** Wrong table name (`logs` vs `system_logs`)

**Quick Fix:** 
```bash
python fix_authentication.py
# Select option 5
```

**Then Login With:**
- Email: `admin@university.edu` (correct spelling!)
- Password: `admin123`

**Expected Result:** Login succeeds, redirects to `/admin/dashboard.html`

---

**Last Updated:** [Current Date]
**Status:** Fix applied, ready for testing
