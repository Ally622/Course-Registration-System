-- ============================================================
-- FIX LOGS TABLE ISSUE
-- This script fixes the mismatch between 'logs' and 'system_logs'
-- ============================================================

USE course_registration_system;

-- Check current state
SELECT 'Checking current tables...' AS Status;

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'course_registration_system' AND table_name = 'logs')
        THEN 'Old "logs" table exists'
        ELSE 'No "logs" table found'
    END AS logs_status,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'course_registration_system' AND table_name = 'system_logs')
        THEN 'system_logs table exists'
        ELSE 'system_logs table MISSING'
    END AS system_logs_status;

-- ============================================================
-- OPTION 1: If old 'logs' table exists, rename it
-- ============================================================

-- Check if 'logs' exists
SET @old_logs_exists = (
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'course_registration_system' 
    AND table_name = 'logs'
);

-- Rename if it exists
SET @rename_sql = IF(@old_logs_exists > 0, 
    'RENAME TABLE logs TO system_logs_backup',
    'SELECT "No old logs table to rename" AS Info'
);

PREPARE stmt FROM @rename_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Step 1: Renamed old logs table (if existed)' AS Status;

-- ============================================================
-- OPTION 2: Create system_logs table if it doesn't exist
-- ============================================================

CREATE TABLE IF NOT EXISTS system_logs (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,
    action      VARCHAR(100) NOT NULL,
    table_name  VARCHAR(50),
    record_id   INT,
    ip_address  VARCHAR(45),
    description TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_logs_user (user_id),
    INDEX idx_logs_date (created_at),
    INDEX idx_logs_action (action)
) ENGINE=InnoDB;

SELECT 'Step 2: Ensured system_logs table exists' AS Status;

-- ============================================================
-- OPTION 3: Fix column names if needed
-- ============================================================

-- Check if 'new_value' column exists (wrong name)
SET @new_value_exists = (
    SELECT COUNT(*) 
    FROM information_schema.columns 
    WHERE table_schema = 'course_registration_system' 
    AND table_name = 'system_logs'
    AND column_name = 'new_value'
);

-- Check if 'description' column exists (correct name)
SET @description_exists = (
    SELECT COUNT(*) 
    FROM information_schema.columns 
    WHERE table_schema = 'course_registration_system' 
    AND table_name = 'system_logs'
    AND column_name = 'description'
);

-- Rename column if needed
SET @fix_column_sql = CASE
    WHEN @new_value_exists > 0 AND @description_exists = 0 THEN
        'ALTER TABLE system_logs CHANGE new_value description TEXT'
    WHEN @description_exists > 0 THEN
        'SELECT "description column already correct" AS Info'
    ELSE
        'ALTER TABLE system_logs ADD COLUMN description TEXT'
END;

PREPARE stmt FROM @fix_column_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Step 3: Fixed column names' AS Status;

-- ============================================================
-- OPTION 4: Migrate data from backup if it exists
-- ============================================================

SET @backup_exists = (
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'course_registration_system' 
    AND table_name = 'system_logs_backup'
);

SET @migrate_sql = IF(@backup_exists > 0,
    'INSERT INTO system_logs (user_id, action, table_name, record_id, description, created_at)
     SELECT user_id, action, table_name, record_id, 
            COALESCE(new_value, description) as description, 
            created_at
     FROM system_logs_backup
     ON DUPLICATE KEY UPDATE user_id=user_id',
    'SELECT "No backup data to migrate" AS Info'
);

PREPARE stmt FROM @migrate_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Step 4: Migrated backup data (if any)' AS Status;

-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT '=== VERIFICATION ===' AS Status;

SELECT 
    table_name,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'course_registration_system'
AND table_name IN ('system_logs', 'logs', 'system_logs_backup')
GROUP BY table_name;

SELECT '=== system_logs COLUMNS ===' AS Status;

SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'course_registration_system'
AND table_name = 'system_logs'
ORDER BY ordinal_position;

SELECT '=== RECORD COUNT ===' AS Status;

SELECT 
    COUNT(*) as total_logs,
    COUNT(DISTINCT user_id) as unique_users,
    MAX(created_at) as latest_log
FROM system_logs;

SELECT '✅ LOGS TABLE FIX COMPLETE!' AS Status;
SELECT 'You can now restart Flask and try logging in again.' AS Next_Step;
