-- ============================================================
-- UNIVERSITY COURSE REGISTRATION SYSTEM - PRODUCTION SCHEMA
-- Final consolidated database structure for production deployment
-- Version: 1.0 (Production Ready)
-- ============================================================

-- ============================================================
-- DATABASE SETUP
-- ============================================================
CREATE DATABASE IF NOT EXISTS course_registration_system
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE course_registration_system;

-- ============================================================
-- 1. USERS - Base Authentication Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role        ENUM('student','admin','lecturer') DEFAULT 'student',
    is_active   TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB;

-- ============================================================
-- 2. ACADEMIC STRUCTURE HIERARCHY
-- ============================================================

-- 2A. SCHOOLS (Top-level academic divisions)
CREATE TABLE IF NOT EXISTS schools (
    school_id   INT AUTO_INCREMENT PRIMARY KEY,
    school_name VARCHAR(150) NOT NULL UNIQUE,
    school_code VARCHAR(10) UNIQUE,
    dean        VARCHAR(100),
    description TEXT,
    established_year YEAR,
    is_active   TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_schools_code (school_code),
    INDEX idx_schools_active (is_active)
) ENGINE=InnoDB;

-- 2B. DEPARTMENTS (Within schools)
CREATE TABLE IF NOT EXISTS departments (
    department_id       INT AUTO_INCREMENT PRIMARY KEY,
    department_name     VARCHAR(100) NOT NULL,
    department_code     VARCHAR(10) NOT NULL,
    school_id           INT NOT NULL,
    hod_name           VARCHAR(100),
    description        TEXT,
    is_active          TINYINT(1) DEFAULT 1,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE,
    UNIQUE KEY uq_dept_code_school (department_code, school_id),
    INDEX idx_departments_school (school_id),
    INDEX idx_departments_active (is_active)
) ENGINE=InnoDB;
-- 2C. PROGRAMMES (Degree programs within departments)
CREATE TABLE IF NOT EXISTS programmes (
    programme_id    INT AUTO_INCREMENT PRIMARY KEY,
    programme_name  VARCHAR(150) NOT NULL,
    programme_code  VARCHAR(15) NOT NULL UNIQUE,
    department_id   INT NOT NULL,
    description     TEXT,
    duration_years  INT DEFAULT 4,
    degree_level    ENUM('certificate','diploma','bachelor','master','phd') DEFAULT 'bachelor',
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,
    INDEX idx_programmes_dept (department_id),
    INDEX idx_programmes_code (programme_code),
    INDEX idx_programmes_active (is_active)
) ENGINE=InnoDB;

-- ============================================================
-- 3. ACADEMIC CALENDAR
-- ============================================================

-- 3A. ACADEMIC SESSIONS
CREATE TABLE IF NOT EXISTS academic_sessions (
    session_id      INT AUTO_INCREMENT PRIMARY KEY,
    session_name    VARCHAR(50) NOT NULL UNIQUE,
    academic_year   VARCHAR(20) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    is_current      TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_sessions_year (academic_year),
    INDEX idx_sessions_current (is_current)
) ENGINE=InnoDB;

-- 3B. SEMESTERS
CREATE TABLE IF NOT EXISTS semesters (
    semester_id             INT AUTO_INCREMENT PRIMARY KEY,
    semester_name           VARCHAR(50) NOT NULL,
    semester_number         TINYINT NOT NULL,
    session_id              INT NOT NULL,
    start_date              DATE NOT NULL,
    end_date                DATE NOT NULL,
    registration_start      DATE NOT NULL,
    registration_deadline   DATE NOT NULL,
    is_active               TINYINT(1) DEFAULT 0,
    is_registration_open    TINYINT(1) DEFAULT 1,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id) REFERENCES academic_sessions(session_id) ON DELETE CASCADE,
    UNIQUE KEY uq_semester_session (semester_number, session_id),
    INDEX idx_semesters_active (is_active),
    INDEX idx_semesters_registration (is_registration_open)
) ENGINE=InnoDB;
-- ============================================================
-- 4. STAFF MANAGEMENT
-- ============================================================

-- 4A. LECTURERS
CREATE TABLE IF NOT EXISTS lecturers (
    lecturer_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNIQUE,
    lecturer_name   VARCHAR(100) NOT NULL,
    staff_id        VARCHAR(20) UNIQUE,
    department_id   INT,
    email           VARCHAR(150),
    phone           VARCHAR(20),
    title           VARCHAR(50),
    qualification   VARCHAR(200),
    specialization  TEXT,
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    INDEX idx_lecturers_staff_id (staff_id),
    INDEX idx_lecturers_dept (department_id),
    INDEX idx_lecturers_active (is_active)
) ENGINE=InnoDB;

-- 4B. ADMINS
CREATE TABLE IF NOT EXISTS admins (
    admin_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    admin_name  VARCHAR(100) NOT NULL,
    staff_id    VARCHAR(20) UNIQUE,
    role_level  ENUM('super_admin','registrar','dean','hod','moderator') DEFAULT 'moderator',
    department_id INT,
    permissions JSON,
    is_active   TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    INDEX idx_admins_role (role_level),
    INDEX idx_admins_active (is_active)
) ENGINE=InnoDB;
-- ============================================================
-- 5. STUDENT MANAGEMENT
-- ============================================================

-- 5A. STUDENTS
CREATE TABLE IF NOT EXISTS students (
    student_id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL UNIQUE,
    registration_number VARCHAR(20) UNIQUE,
    student_name        VARCHAR(100) NOT NULL,
    phone               VARCHAR(20),
    date_of_birth       DATE,
    gender              ENUM('male','female','other'),
    id_number           VARCHAR(20) UNIQUE,
    department_id       INT,
    programme_id        INT,
    year_of_study       INT DEFAULT 1,
    entry_year          YEAR,
    status              ENUM('active','suspended','graduated','withdrawn') DEFAULT 'active',
    profile_photo       VARCHAR(255),
    address             TEXT,
    guardian_name       VARCHAR(100),
    guardian_phone      VARCHAR(20),
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    FOREIGN KEY (programme_id) REFERENCES programmes(programme_id) ON DELETE SET NULL,
    INDEX idx_students_reg_number (registration_number),
    INDEX idx_students_programme (programme_id),
    INDEX idx_students_status (status),
    INDEX idx_students_year (year_of_study)
) ENGINE=InnoDB;

-- 5B. KCSE INFORMATION
CREATE TABLE IF NOT EXISTS kcse_info (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    kcse_year       YEAR NOT NULL,
    index_number    VARCHAR(20) NOT NULL,
    school_name     VARCHAR(150) NOT NULL,
    mean_grade      VARCHAR(5) NOT NULL,
    points          INT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_kcse (student_id),
    INDEX idx_kcse_year (kcse_year)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS kcse_grades (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    subject         VARCHAR(100) NOT NULL,
    grade           VARCHAR(5) NOT NULL,
    points          INT NOT NULL DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_subject (student_id, subject)
) ENGINE=InnoDB;

-- ============================================================
-- 6. PROGRAMME ADMISSION
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    programme_id    INT NOT NULL,
    status          ENUM('pending','approved','rejected','withdrawn') DEFAULT 'pending',
    priority        TINYINT DEFAULT 1,
    applied_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at     DATETIME,
    approved_by     INT,
    remarks         TEXT,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (programme_id) REFERENCES programmes(programme_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    INDEX idx_applications_status (status),
    INDEX idx_applications_date (applied_at)
) ENGINE=InnoDB;

-- ============================================================
-- 7. ACADEMIC UNITS (Individual subjects within programmes)
-- ============================================================
CREATE TABLE IF NOT EXISTS units (
    unit_id         INT AUTO_INCREMENT PRIMARY KEY,
    unit_code       VARCHAR(20) NOT NULL UNIQUE,
    unit_name       VARCHAR(150) NOT NULL,
    credit_hours    INT NOT NULL DEFAULT 3,
    programme_id    INT NOT NULL,
    lecturer_id     INT,
    semester_number TINYINT NOT NULL DEFAULT 1,
    year_of_study   TINYINT NOT NULL DEFAULT 1,
    is_elective     TINYINT(1) DEFAULT 0,
    max_capacity    INT DEFAULT 100,
    description     TEXT,
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (programme_id) REFERENCES programmes(programme_id) ON DELETE CASCADE,
    FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id) ON DELETE SET NULL,
    INDEX idx_units_programme (programme_id),
    INDEX idx_units_code (unit_code),
    INDEX idx_units_lecturer (lecturer_id),
    INDEX idx_units_year_semester (year_of_study, semester_number),
    INDEX idx_units_active (is_active)
) ENGINE=InnoDB;

-- Unit Prerequisites
CREATE TABLE IF NOT EXISTS prerequisites (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    unit_id                 INT NOT NULL,
    prerequisite_unit_id    INT NOT NULL,
    is_mandatory            TINYINT(1) DEFAULT 1,

    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    UNIQUE KEY uq_prerequisite (unit_id, prerequisite_unit_id)
) ENGINE=InnoDB;

-- ============================================================
-- 8. UNIT REGISTRATION
-- ============================================================
CREATE TABLE IF NOT EXISTS registrations (
    registration_id     INT AUTO_INCREMENT PRIMARY KEY,
    student_id          INT NOT NULL,
    unit_id             INT NOT NULL,
    semester_id         INT NOT NULL,
    registration_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    status              ENUM('pending','approved','rejected','dropped','completed') DEFAULT 'pending',
    approved_by         INT,
    approved_at         DATETIME,
    dropped_at          DATETIME,
    remarks             TEXT,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    UNIQUE KEY uq_registration (student_id, unit_id, semester_id),
    INDEX idx_registrations_student (student_id),
    INDEX idx_registrations_semester (semester_id),
    INDEX idx_registrations_status (status)
) ENGINE=InnoDB;

-- ============================================================
-- 9. ACADEMIC RESULTS
-- ============================================================
CREATE TABLE IF NOT EXISTS results (
    result_id       INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    unit_id         INT NOT NULL,
    semester_id     INT NOT NULL,
    cat_marks       DECIMAL(5,2) DEFAULT 0,
    exam_marks      DECIMAL(5,2) DEFAULT 0,
    total_marks     DECIMAL(5,2) DEFAULT 0,
    grade           VARCHAR(5),
    grade_points    DECIMAL(3,2) DEFAULT 0.00,
    remarks         TEXT,
    is_published    TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id) ON DELETE CASCADE,
    UNIQUE KEY uq_result (student_id, unit_id, semester_id),
    INDEX idx_results_student (student_id),
    INDEX idx_results_semester (semester_id),
    INDEX idx_results_published (is_published)
) ENGINE=InnoDB;

-- ============================================================
-- 10. TIMETABLE MANAGEMENT
-- ============================================================
CREATE TABLE IF NOT EXISTS timetables (
    timetable_id    INT AUTO_INCREMENT PRIMARY KEY,
    unit_id         INT NOT NULL,
    semester_id     INT NOT NULL,
    day_of_week     ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    venue           VARCHAR(100),
    session_type    ENUM('lecture','tutorial','practical','exam') DEFAULT 'lecture',
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (unit_id) REFERENCES units(unit_id) ON DELETE CASCADE,
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id) ON DELETE CASCADE,
    INDEX idx_timetables_unit (unit_id),
    INDEX idx_timetables_day (day_of_week),
    INDEX idx_timetables_semester (semester_id)
) ENGINE=InnoDB;

-- ============================================================
-- 11. COMMUNICATION SYSTEM
-- ============================================================

-- 11A. ANNOUNCEMENTS
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id     INT AUTO_INCREMENT PRIMARY KEY,
    title               VARCHAR(200) NOT NULL,
    message             TEXT NOT NULL,
    target_audience     ENUM('all','students','lecturers','admins') DEFAULT 'all',
    priority            ENUM('low','normal','high','urgent') DEFAULT 'normal',
    posted_by           INT,
    is_published        TINYINT(1) DEFAULT 1,
    date_posted         DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date         DATETIME,

    FOREIGN KEY (posted_by) REFERENCES admins(admin_id) ON DELETE SET NULL,
    INDEX idx_announcements_audience (target_audience),
    INDEX idx_announcements_published (is_published),
    INDEX idx_announcements_date (date_posted)
) ENGINE=InnoDB;

-- 11B. NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    message         TEXT,
    type            ENUM('info','success','warning','error') DEFAULT 'info',
    is_read         TINYINT(1) DEFAULT 0,
    action_url      VARCHAR(255),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_read (is_read)
) ENGINE=InnoDB;

-- ============================================================
-- 12. SYSTEM MANAGEMENT
-- ============================================================

-- 12A. PASSWORD RESET TOKENS
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  DATETIME NOT NULL,
    used_at     DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_tokens_user (user_id),
    INDEX idx_tokens_expiry (expires_at)
) ENGINE=InnoDB;

-- 12B. SYSTEM LOGS
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

-- ============================================================
-- SYSTEM CONFIGURATION
-- ============================================================
CREATE TABLE IF NOT EXISTS system_settings (
    setting_id    INT AUTO_INCREMENT PRIMARY KEY,
    setting_key   VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    description   TEXT,
    is_public     TINYINT(1) DEFAULT 0,
    updated_by    INT,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (updated_by) REFERENCES admins(admin_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- SUCCESS MESSAGE
-- ============================================================
SELECT 'University Course Registration System - Production Database Schema Created Successfully!' AS status,
       'All tables created with proper relationships, indexes, and constraints' AS details;