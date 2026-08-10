-- ============================================================
-- VERIFY AND POPULATE PROGRAMMES TABLE
-- This script checks if programmes exist and adds sample data if needed
-- ============================================================

USE course_registration_system;

-- Check if programmes table exists
SELECT 'Checking programmes table...' AS Status;

SELECT COUNT(*) AS table_exists 
FROM information_schema.tables 
WHERE table_schema = 'course_registration_system' 
AND table_name = 'programmes';

-- Check current programmes count
SELECT COUNT(*) AS current_programmes_count FROM programmes;

-- Display existing programmes
SELECT 
    p.programme_id,
    p.programme_name,
    p.programme_code,
    p.duration_years,
    p.is_active,
    d.department_name,
    s.school_name
FROM programmes p
INNER JOIN departments d ON p.department_id = d.department_id
INNER JOIN schools s ON d.school_id = s.school_id
ORDER BY s.school_name, d.department_name, p.programme_name;

-- ============================================================
-- INSERT SAMPLE PROGRAMMES IF TABLE IS EMPTY
-- ============================================================

-- Note: Run this only if the table is empty or missing programmes
-- First, ensure we have schools and departments

-- Check if we have schools
SELECT 'Checking schools...' AS Status;
SELECT school_id, school_name FROM schools;

-- Check if we have departments
SELECT 'Checking departments...' AS Status;
SELECT department_id, department_name, school_id FROM departments;

-- ============================================================
-- SAMPLE PROGRAMMES INSERT
-- Only run if programmes table is empty
-- ============================================================

-- If you need to populate, uncomment and run the following:

/*
-- Computing Programmes (assuming department_id 1 is Computer Science)
INSERT INTO programmes (programme_name, programme_code, department_id, description, duration_years, degree_level, is_active) VALUES
('Bachelor of Science in Computer Science', 'BSC-CS', 1, 'Comprehensive computer science education covering algorithms, software development, and computational theory', 4, 'bachelor', 1),
('Bachelor of Science in Information Technology', 'BSC-IT', 1, 'Information technology programme focusing on networks, databases, and IT infrastructure', 4, 'bachelor', 1),
('Bachelor of Science in Software Engineering', 'BSC-SE', 1, 'Software engineering programme with emphasis on software design, development, and project management', 4, 'bachelor', 1),
('Bachelor of Business Information Technology', 'BBIT', 1, 'Combines business acumen with IT skills for digital business solutions', 4, 'bachelor', 1);

-- Engineering Programmes (assuming department_id 2)
INSERT INTO programmes (programme_name, programme_code, department_id, description, duration_years, degree_level, is_active) VALUES
('Bachelor of Science in Civil Engineering', 'BSC-CE', 2, 'Civil engineering programme covering structural design, construction, and infrastructure', 4, 'bachelor', 1),
('Bachelor of Science in Electrical Engineering', 'BSC-EE', 2, 'Electrical engineering with focus on power systems, electronics, and telecommunications', 4, 'bachelor', 1),
('Bachelor of Science in Mechanical Engineering', 'BSC-ME', 2, 'Mechanical engineering covering thermodynamics, mechanics, and manufacturing', 4, 'bachelor', 1);

-- Business Programmes (assuming department_id 3)
INSERT INTO programmes (programme_name, programme_code, department_id, description, duration_years, degree_level, is_active) VALUES
('Bachelor of Commerce', 'BCOM', 3, 'Commerce degree with specializations in accounting, finance, and marketing', 4, 'bachelor', 1),
('Bachelor of Business Administration', 'BBA', 3, 'Business administration programme covering management, strategy, and entrepreneurship', 4, 'bachelor', 1);
*/

-- ============================================================
-- VERIFICATION QUERY
-- Run this after inserting to verify
-- ============================================================

SELECT 
    s.school_name,
    d.department_name,
    COUNT(p.programme_id) AS programme_count
FROM schools s
LEFT JOIN departments d ON s.school_id = d.school_id
LEFT JOIN programmes p ON d.department_id = p.department_id
GROUP BY s.school_id, s.school_name, d.department_id, d.department_name
ORDER BY s.school_name, d.department_name;

-- Check final count
SELECT COUNT(*) AS total_programmes FROM programmes WHERE is_active = 1;

SELECT 'Verification complete!' AS Status;
