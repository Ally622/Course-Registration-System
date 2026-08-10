"""
Insert results and timetable data for John Doe using Python (MariaDB compatible).
"""
import sys
sys.path.insert(0, '.')
from db import get_connection

RESULTS = [
    # unit_code, cat_marks, exam_marks
    ('CS101', 28.5, 49.5),   # total=78 → A
    ('CS102', 24.0, 48.0),   # total=72 → A
    ('CS103', 26.0, 43.0),   # total=69 → B
    ('CS104', 22.5, 50.0),   # total=72.5 → A
    ('CS105', 27.0, 44.5),   # total=71.5 → A
    ('CS106', 18.0, 38.5),   # total=56.5 → C
    ('CS107', 16.5, 42.0),   # total=58.5 → C
]

TIMETABLE = [
    # unit_code, day, start, end, venue
    ('CS101', 'Monday',    '08:00:00', '10:00:00', 'LH-101 Lecture Hall'),
    ('CS102', 'Monday',    '10:00:00', '12:00:00', 'LH-102 Lecture Hall'),
    ('CS103', 'Tuesday',   '08:00:00', '10:00:00', 'LH-103 Lecture Hall'),
    ('CS104', 'Tuesday',   '10:00:00', '12:00:00', 'LH-201 Lecture Hall'),
    ('CS105', 'Wednesday', '08:00:00', '10:00:00', 'Lab-01 Computer Lab'),
    ('CS106', 'Wednesday', '10:00:00', '11:00:00', 'LH-101 Lecture Hall'),
    ('CS107', 'Thursday',  '08:00:00', '09:00:00', 'LH-102 Lecture Hall'),
]

def grade(total):
    if total >= 70: return 'A', 4.00
    if total >= 60: return 'B', 3.00
    if total >= 50: return 'C', 2.00
    if total >= 40: return 'D', 1.00
    return 'F', 0.00

def remarks(g):
    return {'A': 'Distinction', 'B': 'Credit', 'C': 'Pass', 'D': 'Pass', 'F': 'Fail'}[g]

conn = get_connection()
cur = conn.cursor(dictionary=True)

# Clear existing
cur.execute("DELETE FROM results WHERE student_id=1 AND semester_id=1")
print(f"Cleared old results")

# Get unit_id map
cur.execute("SELECT unit_id, unit_code FROM units WHERE programme_id=1 AND year_of_study=1 AND semester_number=1")
unit_map = {r['unit_code']: r['unit_id'] for r in cur.fetchall()}
print(f"Unit map: {unit_map}")

# Insert results
for code, cat, exam in RESULTS:
    uid = unit_map.get(code)
    if not uid:
        print(f"  SKIP {code} — not in unit_map")
        continue
    total = round(cat + exam, 1)
    g, gp = grade(total)
    rem = remarks(g)
    cur.execute("""
        INSERT INTO results
            (student_id, unit_id, semester_id, cat_marks, exam_marks,
             total_marks, grade, grade_points, remarks, is_published)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE
            cat_marks=%s, exam_marks=%s, total_marks=%s,
            grade=%s, grade_points=%s, remarks=%s, is_published=1
    """, (1, uid, 1, cat, exam, total, g, gp, rem,
          cat, exam, total, g, gp, rem))
    print(f"  Result: {code} CAT={cat} Exam={exam} Total={total} Grade={g}")

conn.commit()
print("Results inserted.")

# Clear existing timetable for these units
unit_ids = list(unit_map.values())
if unit_ids:
    placeholders = ','.join(['%s'] * len(unit_ids))
    cur.execute(f"DELETE FROM timetables WHERE semester_id=1 AND unit_id IN ({placeholders})", unit_ids)

# Insert timetable
for code, day, start, end, venue in TIMETABLE:
    uid = unit_map.get(code)
    if not uid:
        print(f"  SKIP timetable {code}")
        continue
    cur.execute("""
        INSERT INTO timetables
            (unit_id, semester_id, day_of_week, start_time, end_time, venue, session_type, is_active)
        VALUES (%s, 1, %s, %s, %s, %s, 'lecture', 1)
    """, (uid, day, start, end, venue))
    print(f"  Timetable: {code} {day} {start}-{end} {venue}")

conn.commit()
print("Timetable inserted.")

# Confirm
cur.execute("""
    SELECT u.unit_code, r.cat_marks, r.exam_marks, r.total_marks, r.grade, r.remarks
    FROM results r JOIN units u ON r.unit_id=u.unit_id
    WHERE r.student_id=1 ORDER BY u.unit_code
""")
print("\nFinal results:")
total_marks_sum = 0
count = 0
for row in cur.fetchall():
    print(f"  {row['unit_code']}: CAT={row['cat_marks']} Exam={row['exam_marks']} Total={row['total_marks']} Grade={row['grade']} ({row['remarks']})")
    total_marks_sum += float(row['total_marks'])
    count += 1
if count:
    print(f"  Average: {total_marks_sum/count:.1f}%")

cur.close()
conn.close()
print("Done.")
