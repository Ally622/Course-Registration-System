-- =============================================================
-- COURSE REGISTRATION SYSTEM — DATA MIGRATION
-- Adds: 7th unit, approved registrations, results, timetable
-- Safe to re-run (uses INSERT IGNORE / ON DUPLICATE KEY)
-- =============================================================
USE course_registration_system;

-- ─────────────────────────────────────────────────────────────
-- 1. Add 7th unit for BSc CS Year 1 Semester 1
-- ─────────────────────────────────────────────────────────────
INSERT IGNORE INTO units
    (unit_code, unit_name, credit_hours, programme_id, lecturer_id,
     semester_number, year_of_study, is_elective, description, is_active)
VALUES
    ('CS107', 'Computer Ethics & Society', 2, 1, NULL,
     1, 1, 0, 'Ethics in computing: intellectual property, privacy, security, and societal impact of technology', 1);

-- ─────────────────────────────────────────────────────────────
-- 2. Clear any existing registrations for John Doe (clean slate)
-- ─────────────────────────────────────────────────────────────
DELETE FROM registrations WHERE student_id = 1 AND semester_id = 1;

-- ─────────────────────────────────────────────────────────────
-- 3. Register John Doe for 7 Year-1 Sem-1 CS units (APPROVED)
-- ─────────────────────────────────────────────────────────────
INSERT INTO registrations (student_id, unit_id, semester_id, status, registration_date, approved_by, approved_at)
SELECT
    1 AS student_id,
    u.unit_id,
    1 AS semester_id,
    'approved' AS status,
    '2026-09-15 09:00:00' AS registration_date,
    1 AS approved_by,
    '2026-09-16 10:00:00' AS approved_at
FROM units u
WHERE u.programme_id = 1
  AND u.year_of_study = 1
  AND u.semester_number = 1
  AND u.is_active = 1
ORDER BY u.unit_code;

-- ─────────────────────────────────────────────────────────────
-- 4. Register Jane Smith (student_id=2) for IT Year-1 Sem-1 units
-- ─────────────────────────────────────────────────────────────
-- First ensure IT has some units
INSERT IGNORE INTO units
    (unit_code, unit_name, credit_hours, programme_id, lecturer_id,
     semester_number, year_of_study, is_elective, description, is_active)
VALUES
    ('IT101', 'Introduction to Information Technology', 4, 2, NULL, 1, 1, 0, 'Overview of IT infrastructure, hardware, software and networks', 1),
    ('IT102', 'IT Mathematics', 3, 2, NULL, 1, 1, 0, 'Discrete mathematics and logic for IT students', 1),
    ('IT103', 'Database Fundamentals', 4, 2, NULL, 1, 1, 0, 'Introduction to relational databases, SQL and data modelling', 1),
    ('IT104', 'Web Technologies', 3, 2, NULL, 1, 1, 0, 'HTML, CSS, JavaScript and basic web development', 1),
    ('IT105', 'Networking Basics', 3, 2, NULL, 1, 1, 0, 'OSI model, TCP/IP, LAN/WAN infrastructure', 1),
    ('IT106', 'Operating Systems Fundamentals', 3, 2, NULL, 1, 1, 0, 'Windows and Linux administration, file systems and processes', 1),
    ('IT107', 'Communication Skills for IT', 2, 2, NULL, 1, 1, 0, 'Technical writing, presentation and professional communication', 1);

DELETE FROM registrations WHERE student_id = 2 AND semester_id = 1;

INSERT INTO registrations (student_id, unit_id, semester_id, status, registration_date, approved_by, approved_at)
SELECT
    2, u.unit_id, 1, 'approved',
    '2026-09-15 09:30:00', 1, '2026-09-16 10:30:00'
FROM units u
WHERE u.programme_id = 2
  AND u.year_of_study = 1
  AND u.semester_number = 1
  AND u.is_active = 1
ORDER BY u.unit_code;

-- ─────────────────────────────────────────────────────────────
-- 5. Clear existing results for John Doe and add fresh results
-- ─────────────────────────────────────────────────────────────
DELETE FROM results WHERE student_id = 1 AND semester_id = 1;

INSERT INTO results (student_id, unit_id, semester_id, cat_marks, exam_marks, total_marks, grade, grade_points, is_published)
SELECT
    1 AS student_id,
    u.unit_id,
    1 AS semester_id,
    cat.cat_marks,
    exam.exam_marks,
    ROUND(cat.cat_marks + exam.exam_marks, 1) AS total_marks,
    CASE
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 70 THEN 'A'
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 60 THEN 'B'
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 50 THEN 'C'
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 40 THEN 'D'
        ELSE 'F'
    END AS grade,
    CASE
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 70 THEN 4.00
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 60 THEN 3.00
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 50 THEN 2.00
        WHEN ROUND(cat.cat_marks + exam.exam_marks, 1) >= 40 THEN 1.00
        ELSE 0.00
    END AS grade_points,
    1 AS is_published
FROM units u
JOIN (
    -- CAT marks per unit code
    SELECT unit_code, cat_marks FROM (
        VALUES
        ROW('CS101', 28.5),
        ROW('CS102', 24.0),
        ROW('CS103', 26.0),
        ROW('CS104', 22.5),
        ROW('CS105', 27.0),
        ROW('CS106', 18.0),
        ROW('CS107', 16.5)
    ) AS t(unit_code, cat_marks)
) cat ON u.unit_code = cat.unit_code
JOIN (
    -- Exam marks per unit code
    SELECT unit_code, exam_marks FROM (
        VALUES
        ROW('CS101', 49.5),
        ROW('CS102', 48.0),
        ROW('CS103', 43.0),
        ROW('CS104', 50.0),
        ROW('CS105', 44.5),
        ROW('CS106', 38.5),
        ROW('CS107', 42.0)
    ) AS t(unit_code, exam_marks)
) exam ON u.unit_code = exam.unit_code
WHERE u.programme_id = 1
  AND u.year_of_study = 1
  AND u.semester_number = 1
  AND u.is_active = 1;

-- ─────────────────────────────────────────────────────────────
-- 6. Add timetable entries for John Doe's 7 units
-- ─────────────────────────────────────────────────────────────
DELETE FROM timetables WHERE semester_id = 1 AND unit_id IN (
    SELECT unit_id FROM units WHERE programme_id = 1 AND year_of_study = 1 AND semester_number = 1
);

INSERT IGNORE INTO timetables (unit_id, semester_id, day_of_week, start_time, end_time, venue, session_type, is_active)
SELECT u.unit_id, 1, t.day_of_week, t.start_time, t.end_time, t.venue, 'lecture', 1
FROM units u
JOIN (
    VALUES
    ROW('CS101', 'Monday',    '08:00:00', '10:00:00', 'LH-101 Lecture Hall'),
    ROW('CS102', 'Monday',    '10:00:00', '12:00:00', 'LH-102 Lecture Hall'),
    ROW('CS103', 'Tuesday',   '08:00:00', '10:00:00', 'LH-103 Lecture Hall'),
    ROW('CS104', 'Tuesday',   '10:00:00', '12:00:00', 'LH-201 Lecture Hall'),
    ROW('CS105', 'Wednesday', '08:00:00', '10:00:00', 'Lab-01 Computer Lab'),
    ROW('CS106', 'Wednesday', '10:00:00', '11:00:00', 'LH-101 Lecture Hall'),
    ROW('CS107', 'Thursday',  '08:00:00', '09:00:00', 'LH-102 Lecture Hall')
) AS t(unit_code, day_of_week, start_time, end_time, venue)
ON u.unit_code = t.unit_code
WHERE u.programme_id = 1 AND u.year_of_study = 1 AND u.semester_number = 1;

-- ─────────────────────────────────────────────────────────────
-- 7. Ensure John Doe has an approved application for BSc CS
-- ─────────────────────────────────────────────────────────────
INSERT IGNORE INTO applications (student_id, programme_id, status, priority, applied_at, reviewed_at, approved_by)
VALUES (1, 1, 'approved', 1, '2026-08-01 09:00:00', '2026-08-10 10:00:00', 1);

-- Ensure programme_id is set on the student row
UPDATE students SET programme_id = 1, department_id = 1, year_of_study = 1 WHERE student_id = 1;
UPDATE students SET programme_id = 2, department_id = 2, year_of_study = 1 WHERE student_id = 2;

-- ─────────────────────────────────────────────────────────────
-- 8. Add a sample announcement
-- ─────────────────────────────────────────────────────────────
INSERT IGNORE INTO announcements (title, message, target_audience, priority, posted_by, is_published, date_posted)
VALUES
    ('Semester 1 Registration Complete', 'All students have been successfully registered for Semester 1 units. Please check your timetable and prepare accordingly.', 'students', 'normal', 1, 1, '2026-09-16 09:00:00'),
    ('CAT 1 Schedule Released', 'The Continuous Assessment Test 1 schedule has been released. Check your course timetable for dates.', 'students', 'high', 1, 1, '2026-10-01 09:00:00');

-- ─────────────────────────────────────────────────────────────
-- 9. Verify
-- ─────────────────────────────────────────────────────────────
SELECT 'Registrations for John Doe:' AS info;
SELECT u.unit_code, u.unit_name, r.status FROM registrations r
JOIN units u ON r.unit_id = u.unit_id
WHERE r.student_id = 1 ORDER BY u.unit_code;

SELECT 'Results for John Doe:' AS info;
SELECT u.unit_code, r.cat_marks, r.exam_marks, r.total_marks, r.grade FROM results r
JOIN units u ON r.unit_id = u.unit_id
WHERE r.student_id = 1 ORDER BY u.unit_code;

SELECT 'Timetable entries:' AS info;
SELECT u.unit_code, t.day_of_week, t.start_time, t.venue FROM timetables t
JOIN units u ON t.unit_id = u.unit_id
WHERE t.semester_id = 1 ORDER BY t.day_of_week, t.start_time;
