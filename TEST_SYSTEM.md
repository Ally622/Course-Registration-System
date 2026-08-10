# Course Registration System - Complete Testing Guide

## Prerequisites

1. **MySQL Server Running**
   ```bash
   # Check if MySQL is running
   # Windows: Check Services or run
   mysqld --version
   ```

2. **Database Setup**
   ```bash
   # Login to MySQL
   mysql -u root -p
   
   # Create database if not exists
   CREATE DATABASE IF NOT EXISTS course_registration;
   
   # Use the database
   USE course_registration;
   
   # Run schema
   SOURCE path/to/database/schema.sql;
   
   # Run seed data
   SOURCE path/to/database/seed_data.sql;
   ```

3. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Start the System

```bash
# Navigate to project directory
cd "c:\Users\CHEMOGET\Desktop\3.1\software engineering\COURSE_REGISTRATION_SYSTEM\Course_Registration"

# Start Flask server
python app.py
```

**Expected Output:**
```
=======================================================
  Course Registration System
  Running on: http://127.0.0.1:5000
=======================================================

  API Endpoints:
  Auth:         /auth/login, /auth/register, /auth/logout
  Dashboard:    /student/dashboard
  Profile:      /student/profile
  Results:      /student/results
  Timetable:    /student/timetable
  Registration: /registration/courses, /registration/register
  Admin:        /admin/dashboard, /admin/students, ...
  Health:       /api/health
=======================================================
```

## Testing Checklist

### Phase 1: Basic Connectivity

- [ ] **Health Check**
  - URL: `http://127.0.0.1:5000/api/health`
  - Expected: `{"success": true, "message": "Course Registration System is running.", "version": "1.0.0"}`

- [ ] **Landing Page**
  - URL: `http://127.0.0.1:5000/`
  - Expected: Home page loads with navigation

### Phase 2: Authentication

- [ ] **Register New Student**
  - URL: `http://127.0.0.1:5000/register.html`
  - Fill form:
    - Name: Test Student
    - Email: test@student.edu
    - Phone: 0700000000
    - Password: test123
  - Expected: Redirects to dashboard after registration

- [ ] **Login with Test Account**
  - URL: `http://127.0.0.1:5000/login.html`
  - Use: `test@student.edu / test123`
  - Expected: Redirects to student dashboard

- [ ] **Login with Seeded Admin**
  - Use: `admin@university.edu / admin123`
  - Expected: Redirects to admin dashboard

### Phase 3: Student Dashboard

- [ ] **Dashboard Loads**
  - URL: `http://127.0.0.1:5000/student/dashboard.html`
  - Expected: 
    - Welcome message with student name
    - Statistics cards (Registered Units, GPA, Notifications, Semester)
    - Announcements section
    - Quick actions buttons

- [ ] **Sidebar Navigation**
  - Check all links work:
    - [ ] Dashboard
    - [ ] Unit Registration
    - [ ] My Course Units
    - [ ] Results
    - [ ] Timetable
    - [ ] History
    - [ ] Profile

### Phase 4: Unit Registration (CRITICAL)

- [ ] **Navigate to Unit Registration**
  - Click "Unit Registration" in sidebar
  - URL: `http://127.0.0.1:5000/student/courses.html`

- [ ] **Units Load Successfully**
  - Expected:
    - Table appears with course list
    - Columns: Checkbox, Code, Course Name, Credits, Programme, Lecturer
    - No "Failed to load courses" error

- [ ] **Search Functionality**
  - Type in search box
  - Expected: Results filter dynamically

- [ ] **Select Units**
  - Click checkboxes to select units
  - Expected: 
    - Selected count updates
    - Rows highlight in pink
    - Register button enables

- [ ] **Register for Units**
  - Click "Register Selected"
  - Expected:
    - Success toast: "Registration successful! Awaiting approval."
    - Selected units clear
    - Can register again

### Phase 5: My Units

- [ ] **View Registered Units**
  - URL: `http://127.0.0.1:5000/student/my-courses.html`
  - Expected: Shows previously registered units

### Phase 6: Other Pages

- [ ] **Profile Page**
  - URL: `http://127.0.0.1:5000/student/profile.html`
  - Expected: Shows student information

- [ ] **Results Page**
  - URL: `http://127.0.0.1:5000/student/results.html`
  - Expected: Shows results table (may be empty for new students)

- [ ] **Timetable Page**
  - URL: `http://127.0.0.1:5000/student/timetable.html`
  - Expected: Shows timetable (may be empty)

### Phase 7: Logout

- [ ] **Logout Works**
  - Click logout in sidebar
  - Expected: Redirects to login page
  - Try accessing dashboard: Should redirect to login

## Debugging Common Issues

### Issue 1: "Failed to load courses"

**Check:**
1. Flask console for errors
2. Browser console (F12) for JavaScript errors
3. Network tab - check `/registration/courses` response

**Solutions:**
- Verify student is logged in (session exists)
- Check database has active units:
  ```sql
  SELECT * FROM units WHERE is_active = 1 LIMIT 5;
  ```
- Check student has programme_id:
  ```sql
  SELECT student_id, programme_id FROM students WHERE student_id = 1;
  ```

### Issue 2: 404 Errors

**Check:**
- Flask server is running
- Correct URL structure
- Blueprint registration in `app.py`

### Issue 3: Database Errors

**Check:**
- MySQL server is running
- Database exists and has tables
- `db.py` connection settings match your MySQL config

### Issue 4: Sidebar Not Styled

**Check:**
- `style.css` is loading (check Network tab)
- Bootstrap Icons CDN is accessible
- No CSS syntax errors in console

## Database Verification Queries

```sql
-- Check if units exist
SELECT COUNT(*) FROM units WHERE is_active = 1;

-- Check programmes
SELECT * FROM programmes LIMIT 5;

-- Check students
SELECT s.student_id, s.student_name, s.programme_id, u.email 
FROM students s 
LEFT JOIN users u ON s.user_id = u.user_id 
LIMIT 5;

-- Check registrations
SELECT * FROM registrations LIMIT 5;

-- Check active semester
SELECT * FROM semesters WHERE is_active = 1;
```

## API Endpoint Tests (using browser or Postman)

### After Logging In:

1. **Get Available Courses**
   ```
   GET http://127.0.0.1:5000/registration/courses
   ```
   Expected: `{"success": true, "courses": [...]}`

2. **Get My Registered Units**
   ```
   GET http://127.0.0.1:5000/registration/my-courses
   ```
   Expected: `{"success": true, "courses": [...], "total_credits": N}`

3. **Get Dashboard Data**
   ```
   GET http://127.0.0.1:5000/student/dashboard
   ```
   Expected: JSON with student info, stats, announcements

## Success Criteria

✅ System is FULLY WORKING if:

1. No errors in Flask console
2. No errors in browser console
3. All pages load successfully
4. Sidebar navigation works
5. Unit registration page shows courses
6. Can select and register units
7. Registration saves to database
8. All CRUD operations work

## Next Steps After Testing

1. **Populate More Test Data**
   - Add more programmes
   - Add more units
   - Add lecturers
   - Add timetable entries

2. **Test Admin Portal**
   - Login as admin
   - Approve student registrations
   - Manage courses
   - View reports

3. **Performance Testing**
   - Test with many units
   - Test with many students
   - Check load times

4. **Security Testing**
   - Try accessing pages without login
   - Test SQL injection prevention
   - Test XSS prevention

## Contact Points

If issues persist:
1. Check Flask console output
2. Check browser console (F12)
3. Check MySQL error logs
4. Review the SYSTEM_FIXES_SUMMARY.md file
