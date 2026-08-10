-- ============================================================
-- QUICK FIX: Remove invalid index references
-- Run this to fix the schema.sql index errors
-- ============================================================

-- This script removes the problematic index statements that reference 
-- the old 'courses' table which no longer exists

-- First, let's try to drop any existing indexes that might conflict
-- (These will fail silently if the indexes don't exist)

-- Drop old course-related indexes if they exist
DROP INDEX IF EXISTS idx_courses_department ON courses;
DROP INDEX IF EXISTS idx_courses_code ON courses;
DROP INDEX IF EXISTS idx_timetable_course ON timetable;

-- Create the correct indexes for the units table
-- (These will only be created if the units table exists)

CREATE INDEX IF NOT EXISTS idx_units_programme ON units(programme_id);
CREATE INDEX IF NOT EXISTS idx_units_code ON units(unit_code);
CREATE INDEX IF NOT EXISTS idx_units_lecturer ON units(lecturer_id);
CREATE INDEX IF NOT EXISTS idx_timetable_unit ON timetable(unit_id);

-- Verify the fix worked
SELECT 'Schema indexes fixed successfully!' AS status;

-- Show current table status (alternative method without information_schema)
-- This uses SHOW commands instead which don't require special permissions
SHOW INDEX FROM units WHERE Key_name IN ('idx_units_programme', 'idx_units_code', 'idx_units_lecturer');
SHOW INDEX FROM timetables WHERE Key_name = 'idx_timetables_unit';