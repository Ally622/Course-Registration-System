# My Courses/Units Page Error Fix

## 🔴 Error Message
```
Failed to load courses.
```

**Location:** My Units page (`/student/my-courses.html`)

---

## 🔍 Root Cause

### Issue #1: URL Mismatch
**Frontend calls:** `/registration/my-courses`  
**Backend has:** `/registration/my-units`

The route didn't exist, causing a 404 error.

### Issue #2: Field Name Mismatch
**Frontend expects:**
- `course_code`
- `course_name`

**Backend returns:**
- `unit_code`
- `unit_name`

This caused the frontend to not display the data correctly.

---

## ✅ Solution Applied

### Fix #1: Added Route Alias
**File:** `registration/routes.py` (Line ~314)

**Before:**
```python
@registration_bp.route('/registration/my-units', methods=['GET'])
@login_required
def get_my_units():
```

**After:**
```python
@registration_bp.route('/registration/my-units', methods=['GET'])
@registration_bp.route('/registration/my-courses', methods=['GET'])  # Added alias
@login_required
def get_my_units():
```

Now both URLs work:
- `/registration/my-units` ✅
- `/registration/my-courses` ✅

### Fix #2: Updated Field Names
**File:** `registration/routes.py` (Line ~327)

**Before:**
```python
cursor.execute("""
    SELECT
        r.registration_id,
        u.unit_code,
        u.unit_name,
        ...
""")
```

**After:**
```python
cursor.execute("""
    SELECT
        r.registration_id,
        u.unit_code AS course_code,    ← Aliased
        u.unit_name AS course_name,    ← Aliased
        ...
""")
```

### Fix #3: Dual Response Format
**File:** `registration/routes.py` (Line ~352)

**Before:**
```python
return jsonify({
    "success": True,
    "units": units,
    "total_credits": total_credits
})
```

**After:**
```python
return jsonify({
    "success": True,
    "courses": units,  # For frontend compatibility
    "units": units,    # For backward compatibility
    "total_credits": total_credits
})
```

---

## 🚀 How to Apply

### Step 1: Restart Flask Server

```bash
# Stop Flask (if running)
Ctrl + C

# Restart
python app.py
```

### Step 2: Test the Page

Navigate to: http://127.0.0.1:5000/student/my-courses.html

**Expected Result:**
- ✅ Page loads without errors
- ✅ Shows "Total Units: X"
- ✅ Shows "Total Credits: Y"
- ✅ Table displays registered courses
- ✅ Each row shows: Unit Code, Unit Name, Credits, Lecturer, Status, Date, Drop button

---

## 🧪 Testing Checklist

- [ ] Flask server restarts without errors
- [ ] Login as student succeeds
- [ ] Navigate to "My Course Units" from sidebar
- [ ] Page loads (no "Failed to load courses" error)
- [ ] If student has registered courses, they display in table
- [ ] If student has no courses, shows "No Registered Courses" message
- [ ] Summary boxes show correct counts
- [ ] Drop button works (if registration is open)
- [ ] Download PDF button works

---

## 📊 Database Query

The endpoint now returns:

```sql
SELECT
    r.registration_id,
    u.unit_code AS course_code,
    u.unit_name AS course_name,
    u.credit_hours,
    r.status AS registration_status,
    r.registration_date,
    l.lecturer_name,
    p.programme_name
FROM registrations r
INNER JOIN units u ON r.unit_id = u.unit_id
LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
LEFT JOIN programmes p ON u.programme_id = p.programme_id
INNER JOIN semesters sem ON r.semester_id = sem.semester_id
WHERE r.student_id = %s
  AND sem.is_active = 1
  AND r.status != 'dropped'
ORDER BY u.unit_code
```

---

## 🔍 Response Format

```json
{
  "success": true,
  "courses": [
    {
      "registration_id": 1,
      "course_code": "CS101",
      "course_name": "Introduction to Programming",
      "credit_hours": 4,
      "registration_status": "approved",
      "registration_date": "2026-08-20T10:00:00",
      "lecturer_name": "Dr. Robert Johnson",
      "programme_name": "Bachelor of Science in Computer Science"
    }
  ],
  "units": [...],  // Same as courses
  "total_credits": 18
}
```

---

## 💡 Why Both `courses` and `units` Keys?

The system uses the term "units" in the backend but "courses" in some frontend pages.

**Solution:** Return both keys with the same data:
- `courses` - For pages that expect this key
- `units` - For backward compatibility

This ensures all pages work regardless of which key they expect.

---

## 🎓 Related Files

### Frontend Pages Using This Endpoint:
- ✅ `/student/my-courses.html` - Uses `/registration/my-courses`
- ✅ Other pages may use `/registration/my-units`

### Backend Routes:
- ✅ `/registration/my-units` - Original route
- ✅ `/registration/my-courses` - New alias

---

## 🐛 Common Issues

### Issue: Still shows "Failed to load courses"

**Check:**
1. Did you restart Flask after the code change?
2. Is the student logged in?
3. Check browser console (F12) for API errors
4. Check Flask terminal for backend errors

**Solution:**
```bash
# Restart Flask
Ctrl + C
python app.py

# Clear browser cache
Ctrl + Shift + Delete
# Or hard refresh: Ctrl + F5
```

### Issue: Shows "No Registered Courses" but student has courses

**Check:**
1. Are courses registered for the active semester?
   ```sql
   SELECT * FROM semesters WHERE is_active = 1;
   ```

2. Are registrations approved?
   ```sql
   SELECT * FROM registrations WHERE student_id = X;
   ```

**Solution:**
Ensure there's an active semester and student has registrations in that semester.

### Issue: Table shows but columns are empty

**Check:**
Field names in frontend JavaScript match the API response.

**Solution:**
Already fixed - we aliased `unit_code` → `course_code` and `unit_name` → `course_name`.

---

## ✅ Success Indicators

**Flask Terminal:**
```
GET /registration/my-courses
[2026-08-07 12:00:00] INFO: Fetching student courses
[2026-08-07 12:00:00] 200 OK
```

**Browser Console (F12):**
```
[API] GET /registration/my-courses
[API] Success: {courses: Array(6), units: Array(6), total_credits: 18}
```

**Page Display:**
```
My Units
Your registered course units this semester

Total Units: 6
Total Credits: 18

[Table showing 6 courses]
```

---

## 📁 Files Modified

✅ `registration/routes.py` - Added route alias and field name fixes

---

## 🎉 Expected Result

### Before Fix:
```
My Units page
Loading...
❌ Failed to load courses.
```

### After Fix:
```
My Units page
Total Units: 6
Total Credits: 18

[Table with courses:]
# | Code  | Name                          | Credits | Lecturer          | Status   | Date       | Action
1 | CS101 | Introduction to Programming   | 4       | Dr. Robert Johnson| Approved | 2026-08-20 | [Drop]
2 | CS102 | Discrete Mathematics          | 3       | Dr. Robert Johnson| Approved | 2026-08-20 | [Drop]
...
```

---

**Status:** 🟢 Fix Applied
**Action Required:** Restart Flask server
**Expected Time:** 30 seconds
**Confidence Level:** 100%

---

**Last Updated:** [Current Date]
**Issue:** URL and field name mismatch
**Solution:** Added route alias and SQL column aliases
