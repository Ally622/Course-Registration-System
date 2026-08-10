-- ============================================================
-- Migration: Complete Redesign of Student Registration and Course Admission
-- ============================================================
-- Run this on an EXISTING database to apply schema changes.
-- Command: mysql -u root -p course_registration_system < migration_admission.sql
-- ============================================================

USE course_registration_system;

-- 1. Create Programmes Table
CREATE TABLE IF NOT EXISTS programmes (
    programme_id       INT AUTO_INCREMENT PRIMARY KEY,
    programme_name     VARCHAR(200) NOT NULL,
    programme_prefix   VARCHAR(10) NOT NULL,
    department_id      INT NOT NULL,
    description        TEXT,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 2. Add programme_id to students table (Safely)
DROP PROCEDURE IF EXISTS AddProgrammeIdColumn;
DELIMITER //
CREATE PROCEDURE AddProgrammeIdColumn()
BEGIN
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'students'
        AND COLUMN_NAME = 'programme_id'
    ) THEN
        ALTER TABLE students
            ADD COLUMN programme_id INT DEFAULT NULL AFTER department_id,
            ADD CONSTRAINT fk_student_programme FOREIGN KEY (programme_id) REFERENCES programmes(programme_id) ON DELETE SET NULL;
    END IF;
END //
DELIMITER ;
CALL AddProgrammeIdColumn();
DROP PROCEDURE AddProgrammeIdColumn;

-- 3. Create KCSE Info Table
CREATE TABLE IF NOT EXISTS kcse_info (
    student_id      INT PRIMARY KEY,
    kcse_year       INT NOT NULL,
    index_number    VARCHAR(50),
    mean_grade      VARCHAR(5) NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Create KCSE Grades Table
CREATE TABLE IF NOT EXISTS kcse_grades (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    subject         VARCHAR(100) NOT NULL,
    grade           VARCHAR(5) NOT NULL,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_subject (student_id, subject)
) ENGINE=InnoDB;

-- 5. Create Applications Table
CREATE TABLE IF NOT EXISTS applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    programme_id    INT NOT NULL,
    status          ENUM('pending','approved','rejected') DEFAULT 'pending',
    applied_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_by     INT DEFAULT NULL,
    approved_at     DATETIME DEFAULT NULL,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (programme_id) REFERENCES programmes(programme_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES admins(admin_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- Seed some default programmes based on existing departments
-- ============================================================
INSERT INTO programmes (programme_name, programme_prefix, department_id, description) VALUES
('Bachelor of Science in Computer Science', 'CS', 1, 'Focuses on software engineering, algorithms, and computing systems.'),
('Bachelor of Science in Information Technology', 'IT', 2, 'Covers network administration, databases, and IT infrastructure.'),
('Bachelor of Science in Mathematics & Computer Science', 'MAT', 3, 'Blends mathematical modeling with computer algorithms.'),
('Bachelor of Science in Civil Engineering', 'CE', 4, 'Design and construction of infrastructure projects.'),
('Bachelor of Science in Mechanical Engineering', 'ME', 5, 'Design, analysis, and manufacturing of mechanical systems.'),
('Bachelor of Business Administration', 'BBA', 8, 'Principles of management, marketing, and business strategy.'),
('Bachelor of Commerce', 'BCOM', 9, 'Focuses on accounting, finance, and economics.'),
('Bachelor of Science in Nursing', 'NUR', 12, 'Prepares students for professional nursing practice.'),
('Bachelor of Science in Public Health', 'PH', 13, 'Focuses on community health and epidemiology.'),
('Bachelor of Science in Agricultural Engineering', 'AGE', 15, 'Application of engineering principles to agriculture.');
