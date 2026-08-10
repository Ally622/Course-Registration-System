-- Migration: Add programme_id column to courses table
-- Run this if you already have a database without programme_id in courses

ALTER TABLE courses 
ADD COLUMN IF NOT EXISTS programme_id INT AFTER department_id,
ADD FOREIGN KEY IF NOT EXISTS (programme_id) REFERENCES programmes(programme_id) ON DELETE SET NULL;
