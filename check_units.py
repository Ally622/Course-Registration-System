"""Check current registrations and add units to reach minimum of 7."""
import sys
sys.path.insert(0, '.')
from db import get_connection

conn = get_connection()
cur = conn.cursor(dictionary=True)

# Check current state for John Doe (CS/2026/0001)
cur.execute("""
    SELECT s.student_id, s.student_name, s.programme_id, s.registration_number
    FROM students s WHERE s.registration_number = 'CS/2026/0001'
""")
student = cur.fetchone()
print(f"Student: {student}")

# Check active semester
cur.execute("SELECT semester_id, semester_name FROM semesters WHERE is_active=1 LIMIT 1")
sem = cur.fetchone()
print(f"Semester: {sem}")

# Check currently registered units
cur.execute("""
    SELECT r.registration_id, u.unit_code, u.unit_name, r.status
    FROM registrations r
    JOIN units u ON r.unit_id = u.unit_id
    WHERE r.student_id = %s AND r.semester_id = %s
    ORDER BY u.unit_code
""", (student['student_id'], sem['semester_id']))
registered = cur.fetchall()
print(f"\nCurrently registered ({len(registered)}):")
for r in registered:
    print(f"  {r['unit_code']} | {r['unit_name']} | {r['status']}")

# Check all available units for programme 1 (BSC-CS)
cur.execute("""
    SELECT unit_id, unit_code, unit_name, credit_hours, year_of_study, semester_number
    FROM units WHERE programme_id = %s AND is_active=1
    ORDER BY year_of_study, semester_number, unit_code
""", (student['programme_id'],))
all_units = cur.fetchall()
print(f"\nAll available units for BSC-CS ({len(all_units)}):")
for u in all_units:
    print(f"  {u['unit_code']} | {u['unit_name']} | Y{u['year_of_study']}S{u['semester_number']}")

cur.close()
conn.close()
