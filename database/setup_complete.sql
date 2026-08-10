-- ============================================================
-- COURSE REGISTRATION SYSTEM — COMPLETE DATABASE SETUP
-- Run this in MySQL/phpMyAdmin to create the database,
-- all tables, and seed data with correct bcrypt hashes.
-- ============================================================

-- Create database if it doesn't exist
DROP DATABASE IF EXISTS course_registration_system;
CREATE DATABASE course_registration_system
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE course_registration_system;

-- ============================================================
-- 1. USERS - Base Authentication Table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role        ENUM('student','admin','lecturer','registrar') DEFAULT 'student',
    is_active   TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB;

-- ============================================================
-- 2. ACADEMIC STRUCTURE
-- ============================================================
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
-- 7. ACADEMIC UNITS
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
-- 10. TIMETABLE
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
-- 11. COMMUNICATION
-- ============================================================
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
-- NOTE: Schema uses 'used' TINYINT column (not 'used_at' DATETIME)
-- to match the auth/routes.py queries: "SET used = 1 WHERE ..."
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  DATETIME NOT NULL,
    used        TINYINT(1) DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_tokens_user (user_id),
    INDEX idx_tokens_expiry (expires_at)
) ENGINE=InnoDB;

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
-- SEED DATA
-- ============================================================

-- --------------------------------------------------------
-- USERS
-- Admin and staff passwords:
--   admin123    → $2b$12$CfsQWmzN1McgloQk6wuZh.APtBPc9GlsBHE/1jZSa3XuQHWw5CsEa
-- Student passwords:
--   student123  → $2b$12$aLB9RbcQ.wdV.XkN2QQbZ.WCwnNmdDVNe8oIdoTwROuxeDc9ZzwxW
-- --------------------------------------------------------

INSERT INTO users (email, password_hash, role, is_active) VALUES
-- Admins (password: admin123)
('admin@university.edu',      '$2b$12$CfsQWmzN1McgloQk6wuZh.APtBPc9GlsBHE/1jZSa3XuQHWw5CsEa', 'admin', 1),
('registrar@university.edu',  '$2b$12$CfsQWmzN1McgloQk6wuZh.APtBPc9GlsBHE/1jZSa3XuQHWw5CsEa', 'registrar', 1),
-- Students (password: student123)
('john.doe@student.edu',      '$2b$12$aLB9RbcQ.wdV.XkN2QQbZ.WCwnNmdDVNe8oIdoTwROuxeDc9ZzwxW', 'student', 1),
('jane.smith@student.edu',    '$2b$12$aLB9RbcQ.wdV.XkN2QQbZ.WCwnNmdDVNe8oIdoTwROuxeDc9ZzwxW', 'student', 1),
('david.wilson@student.edu',  '$2b$12$aLB9RbcQ.wdV.XkN2QQbZ.WCwnNmdDVNe8oIdoTwROuxeDc9ZzwxW', 'student', 1),
-- Lecturers (password: admin123)
('dr.johnson@university.edu',    '$2b$12$CfsQWmzN1McgloQk6wuZh.APtBPc9GlsBHE/1jZSa3XuQHWw5CsEa', 'lecturer', 1),
('prof.williams@university.edu', '$2b$12$CfsQWmzN1McgloQk6wuZh.APtBPc9GlsBHE/1jZSa3XuQHWw5CsEa', 'lecturer', 1);

-- Schools
INSERT INTO schools (school_name, school_code, dean, description, established_year, is_active) VALUES
('School of Computing and Information Technology', 'SCIT', 'Prof. Michael Anderson', 'Leading school in computer science, information technology, and software engineering education', 2005, 1),
('School of Engineering', 'SOE', 'Prof. Sarah Mitchell', 'Excellence in civil, mechanical, and electrical engineering programs', 2003, 1),
('School of Business', 'SOB', 'Dr. Robert Thompson', 'Comprehensive business education with focus on management and commerce', 2008, 1),
('School of Health Sciences', 'SOHS', 'Dr. Emily Davis', 'Medical, nursing, and public health programs', 2010, 1),
('School of Natural Sciences', 'SONS', 'Prof. James Wilson', 'Mathematics, physics, chemistry, and biology programs', 2004, 1);

-- Departments
INSERT INTO departments (department_name, department_code, school_id, hod_name, description, is_active) VALUES
('Computer Science', 'CS', 1, 'Dr. Alan Turing', 'Software development, algorithms, and computational theory', 1),
('Information Technology', 'IT', 1, 'Dr. Grace Hopper', 'Network administration, cybersecurity, and IT management', 1),
('Software Engineering', 'SE', 1, 'Dr. Linus Torvalds', 'Software design, development methodologies, and quality assurance', 1),
('Civil Engineering', 'CE', 2, 'Dr. Isambard Kingdom', 'Infrastructure, construction, and structural engineering', 1),
('Mechanical Engineering', 'ME', 2, 'Dr. James Watt', 'Machine design, thermodynamics, and manufacturing', 1),
('Electrical Engineering', 'EE', 2, 'Dr. Nikola Tesla', 'Electronics, power systems, and telecommunications', 1),
('Business Administration', 'BA', 3, 'Dr. Peter Drucker', 'Management, marketing, and organizational behavior', 1),
('Commerce', 'COM', 3, 'Dr. Adam Smith', 'Accounting, finance, and business law', 1),
('Nursing', 'NUR', 4, 'Dr. Florence Nightingale', 'Clinical nursing and healthcare management', 1),
('Public Health', 'PH', 4, 'Dr. John Snow', 'Epidemiology, health policy, and community health', 1),
('Mathematics', 'MAT', 5, 'Dr. Isaac Newton', 'Pure and applied mathematics', 1),
('Physics', 'PHY', 5, 'Dr. Albert Einstein', 'Classical and modern physics', 1);

-- Programmes
INSERT INTO programmes (programme_name, programme_code, department_id, description, duration_years, degree_level, is_active) VALUES
('Bachelor of Science in Computer Science', 'BSC-CS', 1, 'Comprehensive computer science education covering algorithms, software development, and computational theory', 4, 'bachelor', 1),
('Bachelor of Science in Information Technology', 'BSC-IT', 2, 'IT management, network administration, and information systems', 4, 'bachelor', 1),
('Bachelor of Science in Software Engineering', 'BSC-SE', 3, 'Software design, development, testing, and project management', 4, 'bachelor', 1),
('Bachelor of Engineering in Civil Engineering', 'BENG-CE', 4, 'Civil engineering design, construction, and infrastructure management', 5, 'bachelor', 1),
('Bachelor of Engineering in Mechanical Engineering', 'BENG-ME', 5, 'Mechanical systems design, thermodynamics, and manufacturing processes', 5, 'bachelor', 1),
('Bachelor of Engineering in Electrical Engineering', 'BENG-EE', 6, 'Electrical systems, electronics, and power engineering', 5, 'bachelor', 1),
('Bachelor of Business Administration', 'BBA', 7, 'Business management, marketing, human resources, and entrepreneurship', 4, 'bachelor', 1),
('Bachelor of Commerce', 'BCOM', 8, 'Accounting, finance, banking, and business law', 4, 'bachelor', 1),
('Bachelor of Science in Nursing', 'BSC-NUR', 9, 'Clinical nursing, patient care, and healthcare management', 4, 'bachelor', 1),
('Bachelor of Science in Public Health', 'BSC-PH', 10, 'Epidemiology, health policy, and community health programs', 4, 'bachelor', 1),
('Bachelor of Science in Mathematics', 'BSC-MAT', 11, 'Pure mathematics, applied mathematics, and statistics', 4, 'bachelor', 1),
('Bachelor of Science in Physics', 'BSC-PHY', 12, 'Classical physics, quantum mechanics, and astrophysics', 4, 'bachelor', 1);

-- Academic Calendar
INSERT INTO academic_sessions (session_name, academic_year, start_date, end_date, is_current) VALUES
('2026/2027 Academic Session', '2026/2027', '2026-09-01', '2027-06-30', 1);

INSERT INTO semesters (semester_name, semester_number, session_id, start_date, end_date, registration_start, registration_deadline, is_active, is_registration_open) VALUES
('Semester 1 - 2026/2027', 1, 1, '2026-09-01', '2026-12-20', '2026-08-15', '2026-09-15', 1, 1),
('Semester 2 - 2026/2027', 2, 1, '2027-01-10', '2027-04-30', '2027-01-01', '2027-01-20', 0, 0);

-- Admins
INSERT INTO admins (user_id, admin_name, staff_id, role_level, department_id, is_active) VALUES
(1, 'System Administrator', 'ADM001', 'super_admin', NULL, 1),
(2, 'Registrar Johnson', 'ADM002', 'registrar', NULL, 1);

-- Lecturers
INSERT INTO lecturers (user_id, lecturer_name, staff_id, department_id, email, phone, title, qualification, specialization, is_active) VALUES
(6, 'Dr. Robert Johnson', 'LEC001', 1, 'dr.johnson@university.edu', '+254712345678', 'Senior Lecturer', 'PhD in Computer Science', 'Artificial Intelligence and Machine Learning', 1),
(7, 'Prof. Mary Williams', 'LEC002', 1, 'prof.williams@university.edu', '+254712345679', 'Professor', 'PhD in Software Engineering', 'Distributed Systems and Cloud Computing', 1);

INSERT INTO lecturers (lecturer_name, staff_id, department_id, email, phone, title, qualification, specialization, is_active) VALUES
('Dr. James Brown', 'LEC003', 2, 'dr.brown@university.edu', '+254712345680', 'Lecturer', 'PhD in Information Technology', 'Network Security and Cryptography', 1),
('Dr. Patricia Davis', 'LEC004', 4, 'dr.davis@university.edu', '+254712345681', 'Senior Lecturer', 'PhD in Civil Engineering', 'Structural Engineering', 1),
('Prof. Michael Miller', 'LEC005', 7, 'prof.miller@university.edu', '+254712345682', 'Professor', 'PhD in Business Administration', 'Strategic Management', 1);

-- Students
INSERT INTO students (user_id, registration_number, student_name, phone, date_of_birth, gender, id_number, department_id, programme_id, year_of_study, entry_year, status) VALUES
(3, 'CS/2026/0001', 'John Doe',    '+254722111222', '2003-05-15', 'male',   '12345678', 1, 1, 1, 2026, 'active'),
(4, 'IT/2026/0002', 'Jane Smith',  '+254733222333', '2003-08-20', 'female', '23456789', 2, 2, 1, 2026, 'active'),
(5, NULL,           'David Wilson', '+254744333444', '2004-03-10', 'male',   '34567890', NULL, NULL, 1, 2026, 'active');

-- CS Units
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description, is_active) VALUES
('CS101', 'Introduction to Programming', 4, 1, 1, 1, 1, 0, 'Fundamentals of programming using Python and Java', 1),
('CS102', 'Discrete Mathematics', 3, 1, 1, 1, 1, 0, 'Mathematical foundations for computer science', 1),
('CS103', 'Computer Organization and Architecture', 4, 1, 2, 1, 1, 0, 'Computer hardware architecture and assembly language', 1),
('CS104', 'Introduction to Algorithms', 3, 1, 1, 1, 1, 0, 'Algorithm design, analysis, and complexity', 1),
('CS105', 'Web Development Fundamentals', 3, 1, 2, 1, 1, 0, 'HTML5, CSS3, JavaScript, and responsive design', 1),
('CS106', 'Professional Communication', 2, 1, NULL, 1, 1, 0, 'Technical writing and professional ethics', 1),
('CS111', 'Object-Oriented Programming', 4, 1, 1, 2, 1, 0, 'OOP principles using Java and C++', 1),
('CS112', 'Data Structures and Algorithms', 4, 1, 1, 2, 1, 0, 'Advanced data structures', 1),
('CS113', 'Database Systems', 4, 1, 2, 2, 1, 0, 'Relational database design and SQL', 1),
('CS114', 'Computer Networks', 3, 1, 2, 2, 1, 0, 'Network protocols, TCP/IP, and OSI model', 1),
('CS115', 'Operating Systems', 4, 1, 1, 2, 1, 0, 'OS concepts, process management, and file systems', 1),
('CS116', 'Linear Algebra', 3, 1, NULL, 2, 1, 0, 'Vectors, matrices, eigenvalues, and linear transformations', 1);

-- System Settings
INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('university_name', 'University of Technology', 'Full name of the university', 1),
('registration_open', '1', 'Whether course registration is currently open', 1),
('current_semester', '1', 'Current active semester ID', 0),
('max_units_per_semester', '6', 'Maximum units a student can register per semester', 1),
('min_units_per_semester', '3', 'Minimum units a student must register per semester', 1);

SELECT 'Database course_registration_system created and seeded successfully!' AS status;
SELECT 'Student login: john.doe@student.edu / student123  OR  CS/2026/0001 / student123' AS demo_student;
SELECT 'Admin login:   admin@university.edu / admin123' AS demo_admin;
SELECT 'Registrar login: registrar@university.edu / admin123' AS demo_registrar;
