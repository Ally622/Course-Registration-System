-- ============================================================
-- Migration: Auth & Registration Flow Refactor
-- ============================================================
-- Run this on an EXISTING database to apply schema changes.
-- Command: mysql -u root -p course_registration_system < migration_auth_flow.sql
-- ============================================================

USE course_registration_system;

-- 1. Add department_prefix column to departments table
-- (Commented out because the column already exists in your database)
-- ALTER TABLE departments
--     ADD COLUMN department_prefix VARCHAR(10) DEFAULT NULL
--     AFTER department_name;

-- 2. Populate department_prefix for existing departments
UPDATE departments SET department_prefix = 'CS'    WHERE department_id = 1;   -- Computer Science
UPDATE departments SET department_prefix = 'IT'    WHERE department_id = 2;   -- Information Technology
UPDATE departments SET department_prefix = 'MAT'   WHERE department_id = 3;   -- Mathematics & Modelling
UPDATE departments SET department_prefix = 'CE'    WHERE department_id = 4;   -- Civil Engineering
UPDATE departments SET department_prefix = 'ME'    WHERE department_id = 5;   -- Mechanical Engineering
UPDATE departments SET department_prefix = 'EE'    WHERE department_id = 6;   -- Electrical Engineering
UPDATE departments SET department_prefix = 'MCE'   WHERE department_id = 7;   -- Mechatronic Engineering
UPDATE departments SET department_prefix = 'BA'    WHERE department_id = 8;   -- Business Administration
UPDATE departments SET department_prefix = 'AF'    WHERE department_id = 9;   -- Accounting and Finance
UPDATE departments SET department_prefix = 'PSC'   WHERE department_id = 10;  -- Procurement and Supply Chain
UPDATE departments SET department_prefix = 'HR'    WHERE department_id = 11;  -- Human Resource Management
UPDATE departments SET department_prefix = 'NUR'   WHERE department_id = 12;  -- Nursing
UPDATE departments SET department_prefix = 'PH'    WHERE department_id = 13;  -- Public Health
UPDATE departments SET department_prefix = 'MLS'   WHERE department_id = 14;  -- Medical Laboratory Science
UPDATE departments SET department_prefix = 'AGE'   WHERE department_id = 15;  -- Agricultural Engineering
UPDATE departments SET department_prefix = 'CRS'   WHERE department_id = 16;  -- Crop Science
UPDATE departments SET department_prefix = 'ANS'   WHERE department_id = 17;  -- Animal Science
UPDATE departments SET department_prefix = 'BT'    WHERE department_id = 18;  -- Biotechnology

-- 3. Make registration_number nullable in students table
--    First drop the existing NOT NULL UNIQUE constraint and recreate as nullable UNIQUE
ALTER TABLE students
    MODIFY COLUMN registration_number VARCHAR(50) DEFAULT NULL;

-- Note: The UNIQUE index on registration_number is preserved.
-- NULL values are allowed in UNIQUE columns in MySQL (multiple NULLs are OK).

-- ============================================================
-- DONE — No data is lost. Existing registration numbers remain intact.
-- ============================================================
