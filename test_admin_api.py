"""Test all admin APIs end-to-end."""
import urllib.request
import json
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

BASE = 'http://127.0.0.1:5000'

# Login
payload = json.dumps({'identifier': 'admin@university.edu', 'password': 'admin123'}).encode()
req = urllib.request.Request(BASE + '/auth/login', data=payload, headers={'Content-Type': 'application/json'})
with opener.open(req, timeout=10) as resp:
    d = json.loads(resp.read())
    print('Admin Login:', 'OK' if d.get('success') else 'FAIL', '-', d.get('message',''))

# Dashboard
with opener.open(BASE + '/admin/dashboard', timeout=10) as r:
    d = json.loads(r.read())
    stats = d.get('stats', {})
    sem = d.get('active_semester', {})
    print('\n=== DASHBOARD ===')
    print(f"  Total Students:  {stats.get('total_students', 0)}")
    print(f"  Total Units:     {stats.get('total_units', 0)}")
    print(f"  Registrations:   {stats.get('total_registrations', 0)}")
    print(f"  Pending:         {stats.get('pending_registrations', 0)}")
    print(f"  Lecturers:       {stats.get('total_lecturers', 0)}")
    print(f"  Active Semester: {sem.get('semester_name', 'None')} | Open: {sem.get('is_registration_open', 0)}")

# Students
with opener.open(BASE + '/admin/students', timeout=10) as r:
    d = json.loads(r.read())
    students = d.get('students', [])
    print(f'\n=== STUDENTS ({len(students)} total) ===')
    for s in students[:5]:
        name = s.get('student_name', 'N/A')
        reg = s.get('registration_number', 'N/A')
        prog = s.get('programme_name', 'N/A')
        print(f'  {name} | {reg} | {prog}')

# Courses / Units
with opener.open(BASE + '/admin/courses', timeout=10) as r:
    d = json.loads(r.read())
    courses = d.get('courses', [])
    print(f'\n=== COURSES/UNITS ({len(courses)} total) ===')
    for c in courses[:5]:
        code = c.get('unit_code') or c.get('course_code', 'N/A')
        name = c.get('unit_name') or c.get('course_name', 'N/A')
        print(f'  {code} | {name}')

# Registrations
with opener.open(BASE + '/admin/registrations', timeout=10) as r:
    d = json.loads(r.read())
    regs = d.get('registrations', [])
    print(f'\n=== REGISTRATIONS ({len(regs)} total) ===')
    for reg in regs[:7]:
        sname = reg.get('student_name', 'N/A')
        code = reg.get('unit_code') or reg.get('course_code', 'N/A')
        status = reg.get('status', 'N/A')
        print(f'  {sname} | {code} | {status}')

# Applications
with opener.open(BASE + '/admin/applications', timeout=10) as r:
    d = json.loads(r.read())
    apps = d.get('applications', [])
    print(f'\n=== APPLICATIONS ({len(apps)} total) ===')
    for a in apps[:3]:
        print(f"  {a.get('student_name','N/A')} | {a.get('status','N/A')}")

print('\nAll admin API tests complete.')
