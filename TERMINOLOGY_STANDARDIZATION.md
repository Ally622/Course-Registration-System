# Terminology Standardization - Complete

## Overview
Successfully standardized all terminology from "units" to "courses" throughout the Course Registration System.

## Changes Made

### 1. Backend Routes (`registration/routes.py`)
- ✅ Renamed function `get_units()` → `get_courses()`
- ✅ Renamed function `register_units()` → `register_courses()`
- ✅ Renamed function `get_my_units()` → `get_my_courses()`
- ✅ Renamed function `drop_unit()` → `drop_course()`
- ✅ Updated all error messages from "unit" to "course"
- ✅ Removed dual field support - now only accepts `courses` field
- ✅ Removed route aliases - single clean route per endpoint:
  - `/registration/courses` (GET) - List available courses
  - `/registration/register` (POST) - Register for courses
  - `/registration/my-courses` (GET) - View registered courses
  - `/registration/drop/<id>` (DELETE) - Drop a course

### 2. Frontend Pages

#### Updated Files:
- ✅ `frontend/student/courses.html`
  - Title: "Course Registration"
  - Sidebar: "Course Registration" (not "Unit Registration")
  - JavaScript: Only uses `courses` field from API
  - Removed fallback to `units` field

- ✅ `frontend/student/my-courses.html`
  - Title: "My Courses"
  - Sidebar: "My Courses" (not "My Units" or "My Course Units")
  - Table headers: "Course Code", "Course Name"
  - Summary: "Total Courses"

- ✅ `frontend/student/dashboard.html`
  - Sidebar navigation updated
  - Button text: "View My Courses"

- ✅ All other student pages:
  - `profile.html`
  - `results.html`
  - `timetable.html`
  - `history.html`
  - `notifications.html`
  - All sidebars now consistently show "Course Registration" and "My Courses"

### 3. Deleted Obsolete Files
- ✅ `frontend/student/units.html` - replaced by `courses.html`
- ✅ `frontend/student/my-units.html` - replaced by `my-courses.html`
- ✅ `frontend/student/courses-backup.html` - no longer needed

## Database Schema
**No database changes required** - the database still uses the `units` table internally, which is correct. The terminology change is only in the user-facing interface and API.

## API Endpoints (Final)
```
GET  /registration/courses          - List available courses
POST /registration/register          - Register for courses (expects: { "courses": [1,2,3] })
GET  /registration/my-courses        - View registered courses
DELETE /registration/drop/<id>       - Drop a course
GET  /registration/history           - Registration history
```

## User Experience
Students now see consistent terminology:
- "Course Registration" instead of "Unit Registration"
- "My Courses" instead of "My Units" or "My Course Units"
- "Register for courses" instead of "Register for units"
- "Drop a course" instead of "Drop a unit"

## Why This Matters
The previous system mixed "units" and "courses" terminology, which was confusing:
- Some pages said "Unit Registration"
- Some pages said "My Course Units"
- API returned both `units` and `courses` fields
- Backend had route aliases like `/registration/units` AND `/registration/courses`

Now everything is clean and consistent - students register for **courses**, period.

## Testing Checklist
- [ ] Login as student
- [ ] Navigate to "Course Registration" - verify courses load
- [ ] Select courses and register
- [ ] Navigate to "My Courses" - verify registered courses appear
- [ ] Drop a course - verify it's removed
- [ ] Check all sidebar links work correctly
- [ ] Verify no console errors about missing fields

---
**Date**: 2024
**Status**: ✅ Complete
