-- ============================================================
-- VERIFICATION SCRIPT: Check Index Status
-- Run this separately to verify indexes are correctly set up
-- ============================================================

USE course_registration_system;

-- Check indexes on units table
SELECT 'Indexes on UNITS table:' AS Info;
SHOW INDEX FROM units;

-- Check indexes on timetables table
SELECT 'Indexes on TIMETABLES table:' AS Info;
SHOW INDEX FROM timetables;

-- Check if old 'courses' table still exists (should NOT exist)
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 'GOOD: courses table does not exist (correct)'
        ELSE 'WARNING: courses table still exists (should be renamed to units)'
    END AS Status
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'course_registration_system' 
    AND TABLE_NAME = 'courses';

-- Count records in key tables
SELECT 'Record counts:' AS Info;
SELECT 'units' AS Table_Name, COUNT(*) AS Record_Count FROM units
UNION ALL
SELECT 'programmes', COUNT(*) FROM programmes
UNION ALL
SELECT 'registrations', COUNT(*) FROM registrations
UNION ALL
SELECT 'results', COUNT(*) FROM results
UNION ALL
SELECT 'timetables', COUNT(*) FROM timetables;

SELECT 'Verification complete!' AS Status;
