-- ============================================================
-- MIGRATION: Convert Courses to Units Structure
-- This migration restructures the system so that:
-- - Programmes and Courses are conceptually the same
-- - Units are the individual subjects within a programme/course  
-- - Students register for units (not courses)
-- ============================================================

-- Step 1: Create the new units table
CREATE TABLE IF NOT EXISTS units (
    unit_id         INT AUTO_INCREMENT PRIMARY KEY,
    unit_code       VARCHAR(20) NOT NULL UNIQUE,
    unit_name       VARCHAR(150) NOT NULL,
    credit_hours    INT NOT NULL DEFAULT 3,
    programme_id    INT NOT NULL,
    lecturer_id     INT,
    semester        INT DEFAULT 1,
    year_of_study   INT DEFAULT 1,
    max_capacity    INT DEFAULT 100,
    description     TEXT DEFAULT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (programme_id)  REFERENCES programmes(programme_id)   ON DELETE CASCADE,
    FOREIGN KEY (lecturer_id)   REFERENCES lecturers(lecturer_id)     ON DELETE SET NULL
) ENGINE=InnoDB;

-- Step 2: Migrate existing courses data to units table  
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester, year_of_study, max_capacity, description, created_at)
SELECT course_code, course_name, credit_hours, programme_id, lecturer_id, semester, year_of_study, max_capacity, description, created_at
FROM courses 
WHERE programme_id IS NOT NULL;

-- Step 3: Create temporary backup tables for existing data
CREATE TABLE registrations_backup AS SELECT * FROM registrations;
CREATE TABLE results_backup AS SELECT * FROM results;  
CREATE TABLE timetables_backup AS SELECT * FROM timetables;

-- Step 4: Update registrations table structure
ALTER TABLE registrations DROP FOREIGN KEY registrations_ibfk_2; -- Drop course_id FK
ALTER TABLE registrations CHANGE course_id unit_id INT NOT NULL;
ALTER TABLE registrations ADD CONSTRAINT fk_registrations_unit 
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE;

-- Step 5: Update results table structure  
ALTER TABLE results DROP FOREIGN KEY results_ibfk_2; -- Drop course_id FK
ALTER TABLE results CHANGE course_id unit_id INT NOT NULL;
ALTER TABLE results ADD CONSTRAINT fk_results_unit 
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE;

-- Step 6: Update timetables table structure
ALTER TABLE timetables DROP FOREIGN KEY timetables_ibfk_1; -- Drop course_id FK  
ALTER TABLE timetables CHANGE course_id unit_id INT NOT NULL;
ALTER TABLE timetables ADD CONSTRAINT fk_timetables_unit 
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE;

-- Step 7: Update prerequisites table structure
ALTER TABLE prerequisites DROP FOREIGN KEY prerequisites_ibfk_1;
ALTER TABLE prerequisites DROP FOREIGN KEY prerequisites_ibfk_2;
ALTER TABLE prerequisites CHANGE course_id unit_id INT NOT NULL;
ALTER TABLE prerequisites CHANGE prerequisite_course_id prerequisite_unit_id INT NOT NULL;
ALTER TABLE prerequisites ADD CONSTRAINT fk_prerequisites_unit 
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE;
ALTER TABLE prerequisites ADD CONSTRAINT fk_prerequisites_prereq_unit 
    FOREIGN KEY (prerequisite_unit_id) REFERENCES units(unit_id) ON DELETE CASCADE;

-- Step 8: Clean up - Drop courses table (since units replace it)
-- Note: Only uncomment this after verifying the migration worked
-- DROP TABLE courses;

-- Step 9: Add sample units data for testing
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, semester, year_of_study, max_capacity, description) VALUES
-- Advanced Computer Science units (if they don't exist)
('CS201', 'Systems Programming', 4, 1, 1, 2, 100, 'Low-level programming, system calls, and concurrent programming'),
('CS202', 'Distributed Systems', 4, 1, 1, 2, 100, 'Distributed computing, consensus algorithms, and microservices'),  
('CS203', 'Artificial Intelligence', 4, 1, 1, 2, 100, 'AI algorithms, machine learning, and neural networks'),
('CS204', 'Theory of Computation', 3, 1, 1, 2, 100, 'Finite automata, formal languages, and computability theory')
ON DUPLICATE KEY UPDATE unit_name = VALUES(unit_name);

-- Verification queries - run these to check the migration
-- SELECT COUNT(*) as units_count FROM units;
-- SELECT COUNT(*) as registrations_count FROM registrations;  
-- SELECT COUNT(*) as results_count FROM results;
-- SELECT COUNT(*) as timetables_count FROM timetables;

-- Success message
SELECT 'Migration completed successfully! Courses are now Units.' as status;