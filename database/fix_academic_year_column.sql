-- ============================================================
-- FIX: academic_year Column Issue
-- ============================================================
-- Problem: Code was trying to SELECT academic_year FROM semesters
-- But academic_year is in academic_sessions table, not semesters
-- Solution: Update queries to JOIN with academic_sessions
-- ============================================================

USE course_registration_system;

-- Verification: Show current table structures
SELECT '=== VERIFICATION: academic_sessions table ===' AS Info;
DESCRIBE academic_sessions;

SELECT '=== VERIFICATION: semesters table ===' AS Info;
DESCRIBE semesters;

-- Show relationship
SELECT '=== Current Data ===' AS Info;

SELECT 
    sem.semester_id,
    sem.semester_name,
    sem.session_id,
    sess.academic_year,
    sem.is_active
FROM semesters sem
LEFT JOIN academic_sessions sess ON sem.session_id = sess.session_id;

-- Test query that was failing
SELECT '=== Testing Fixed Query ===' AS Info;

SELECT sem.semester_name, sess.academic_year
FROM semesters sem
LEFT JOIN academic_sessions sess ON sem.session_id = sess.session_id
WHERE sem.is_active = 1
LIMIT 1;

SELECT '✅ FIX VERIFICATION COMPLETE!' AS Status;
SELECT 'The code has been updated to join with academic_sessions table' AS Solution;
SELECT 'Restart Flask server to apply changes' AS Next_Step;
