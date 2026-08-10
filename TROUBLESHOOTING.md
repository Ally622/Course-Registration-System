# Troubleshooting Guide

Quick solutions to common issues.

## Database Issues

### ❌ "Cannot connect to MySQL database"

**Symptoms:**
- Flask won't start
- Error message about database connection

**Solutions:**
1. **Check if MySQL is running:**
   ```bash
   # Windows: Check Services
   # Or try connecting:
   mysql -u root -p
   ```

2. **Verify database exists:**
   ```sql
   SHOW DATABASES;
   # Should see 'course_registration_system'
   ```

3. **Check credentials in config.py:**
   ```python
   DB_HOST = 'localhost'
   DB_USER = 'root'
   DB_PASSWORD = ''  # Your password here
   DB_NAME = 'course_registration_system'
   ```

4. **Create database if missing:**
   ```sql
   CREATE DATABASE course_registration_system;
   USE course_registration_system;
   SOURCE database/schema.sql;
   SOURCE database/seed_data.sql;
   ```

---

### ❌ "Failed to load courses" / No courses appearing

**Cause:** No active units in database

**Solution:**
```bash
# Run verification
python verify_database.py

# Check if units exist
mysql -u root -p
USE course_registration_system;
SELECT COUNT(*) FROM units WHERE is_active = 1;

# If count is 0, load sample data:
SOURCE database/seed_data.sql;
```

---

### ❌ Student has no programme_id

**Cause:** Student record incomplete

**Solution:**
```sql
-- Assign a programme to student
UPDATE students 
SET programme_id = 1 
WHERE student_id = [YOUR_STUDENT_ID];
```

---

## Authentication Issues

### ❌ "Invalid credentials" with correct password

**Cause:** Password hash mismatch or logging error

**Solutions:**
1. **Use correct email format:**
   - Admin: `admin@university.edu`
   - Student: `john.doe@student.edu` OR `CS/2026/0001`

2. **Check if account is active:**
   ```sql
   SELECT * FROM users WHERE email = 'your@email.com';
   -- Check is_active = 1
   ```

3. **Reset password if needed:**
   ```sql
   -- Generate new hash using bcrypt, then:
   UPDATE users 
   SET password_hash = '$2b$12$NEW_HASH_HERE' 
   WHERE email = 'your@email.com';
   ```

---

### ❌ Session expires immediately

**Cause:** SECRET_KEY not set or changing

**Solution:**
- Set a stable SECRET_KEY in config.py
- Don't change it after users log in

---

## Frontend Issues

### ❌ Page shows "404 Not Found"

**Solutions:**
1. **Check Flask is running:**
   ```bash
   python app.py
   # Should see "Running on http://127.0.0.1:5000"
   ```

2. **Check URL is correct:**
   - Correct: `http://127.0.0.1:5000/student/courses.html`
   - Wrong: `http://127.0.0.1:5000/courses.html`

3. **Check file exists:**
   - Verify file is in `frontend/student/` folder

---

### ❌ "Unexpected token '<'" JavaScript error

**Cause:** API endpoint returning HTML instead of JSON

**Solutions:**
1. **Check endpoint exists:**
   - Open Network tab (F12)
   - Look at failed request
   - Verify endpoint is registered in Flask

2. **Check Flask console for errors:**
   - Look for Python tracebacks
   - Fix any blueprint registration issues

---

### ❌ Sidebar not styled / looks plain

**Cause:** CSS not loading

**Solutions:**
1. **Check CSS file exists:**
   ```
   frontend/assets/css/style.css
   ```

2. **Check browser console (F12):**
   - Look for 404 errors on CSS files
   - Verify path in HTML is correct

3. **Hard refresh browser:**
   - Ctrl+F5 (Windows)
   - Cmd+Shift+R (Mac)

---

### ❌ Bootstrap Icons not showing

**Cause:** CDN link blocked or missing

**Solution:**
Check internet connection or add to HTML:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
```

---

## Registration Issues

### ❌ "No active semester found"

**Solution:**
```sql
-- Create an active semester
INSERT INTO academic_sessions (academic_year, start_date, end_date)
VALUES ('2024/2025', '2024-09-01', '2025-06-30');

INSERT INTO semesters (session_id, semester_name, start_date, end_date, registration_deadline, is_registration_open, is_active)
VALUES (LAST_INSERT_ID(), 'Semester 1', '2024-09-01', '2025-01-31', '2024-10-15', 1, 1);
```

---

### ❌ "Registration is closed"

**Solution:**
```sql
UPDATE semesters 
SET is_registration_open = 1,
    registration_deadline = DATE_ADD(NOW(), INTERVAL 30 DAY)
WHERE is_active = 1;
```

---

### ❌ "You must be fully admitted" error

**Cause:** Old code blocking registration

**Solution:**
This should be fixed. If still seeing it:
1. Check `registration/routes.py` line ~58
2. Should NOT have registration_number check
3. Re-download fixed version

---

## API Issues

### ❌ CORS errors in browser console

**Cause:** Cross-origin request blocked

**Solution:**
- Should be fixed with CORS extension
- If issue persists, check extensions.py

---

### ❌ "Method not allowed" (405 error)

**Cause:** Using wrong HTTP method

**Solution:**
Check endpoint method:
- GET for reading
- POST for creating
- PUT for updating
- DELETE for removing

---

## Performance Issues

### ❌ Slow page loading

**Solutions:**
1. **Check database indexes:**
   ```sql
   SHOW INDEX FROM units;
   SHOW INDEX FROM registrations;
   ```

2. **Optimize queries:**
   - Use LIMIT in SQL queries
   - Add pagination for large result sets

3. **Enable browser caching:**
   - Static files should cache
   - Check Network tab

---

### ❌ Flask server crashes

**Cause:** Usually Python error or database issue

**Solutions:**
1. **Check Flask console:**
   - Read full error traceback
   - Note which file/line failed

2. **Check Python version:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask
# Or:
pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'mysql'"
```bash
pip install mysql-connector-python
```

### "ImportError: cannot import name 'auth_bp'"
- Check `auth/__init__.py` exists
- Check blueprint is created in that file

### "OperationalError: (2003, "Can't connect to MySQL server")"
- MySQL server not running
- Wrong host/port in config.py

### "ProgrammingError: (1146, "Table 'course_registration_system.units' doesn't exist")"
- Run schema.sql
- Verify database name is correct

---

## Testing Steps

If nothing works, test systematically:

1. **Test Database:**
   ```bash
   python verify_database.py
   ```

2. **Test Flask Startup:**
   ```bash
   python app.py
   # Should start without errors
   ```

3. **Test Health Endpoint:**
   ```
   Open: http://127.0.0.1:5000/api/health
   Should show: {"success": true, ...}
   ```

4. **Test Login:**
   - Go to login page
   - Use admin@university.edu / admin123
   - Should redirect to dashboard

5. **Test API Directly:**
   ```
   After logging in:
   http://127.0.0.1:5000/registration/courses
   Should return JSON with course list
   ```

---

## Emergency Reset

If everything is broken, start fresh:

1. **Drop and recreate database:**
   ```sql
   DROP DATABASE course_registration_system;
   CREATE DATABASE course_registration_system;
   USE course_registration_system;
   SOURCE database/schema.sql;
   SOURCE database/seed_data.sql;
   ```

2. **Reinstall Python packages:**
   ```bash
   pip uninstall -y -r requirements.txt
   pip install -r requirements.txt
   ```

3. **Clear browser cache:**
   - Ctrl+Shift+Delete
   - Clear all cached data
   - Restart browser

4. **Restart everything:**
   - Stop Flask (Ctrl+C)
   - Restart MySQL
   - Start Flask again
   - Hard refresh browser

---

## Getting Help

If still stuck:

1. **Check Flask console** - Copy full error message
2. **Check browser console** (F12) - Look for JavaScript errors  
3. **Run verify_database.py** - Check database status
4. **Review README.md** - Check setup instructions
5. **Check FINAL_SYSTEM_STATUS.md** - Verify all components

---

## Contact Support

For persistent issues:
1. Document the exact error message
2. Note which steps you've tried
3. Check if issue is in Flask console or browser console
4. Provide relevant log excerpts

---

*Most issues can be resolved by following this guide. The system is stable and well-tested.*
