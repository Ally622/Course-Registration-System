-- ============================================================
-- UNIVERSITY COURSE REGISTRATION SYSTEM - PRODUCTION SEED DATA
-- Initial data for production deployment and testing
-- Version: 1.0 (Production Ready)
-- ============================================================

USE course_registration_system;

-- ============================================================
-- 1. SYSTEM USERS
-- ============================================================

-- Admin User (Password: admin123)
INSERT INTO users (email, password_hash, role, is_active) VALUES
('admin@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'admin', 1),
('registrar@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'admin', 1);

-- Sample Student Users (Password: student123)
INSERT INTO users (email, password_hash, role, is_active) VALUES
('john.doe@student.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'student', 1),
('jane.smith@student.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'student', 1),
('david.wilson@student.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'student', 1);

-- Sample Lecturer Users (Password: lecturer123)
INSERT INTO users (email, password_hash, role, is_active) VALUES
('dr.johnson@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'lecturer', 1),
('prof.williams@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXK92W7W', 'lecturer', 1);

-- ============================================================
-- 2. ACADEMIC STRUCTURE
-- ============================================================

-- Schools
INSERT INTO schools (school_name, school_code, dean, description, established_year, is_active) VALUES
('School of Computing and Information Technology', 'SCIT', 'Prof. Michael Anderson', 'Leading school in computer science, information technology, and software engineering education', 2005, 1),
('School of Engineering', 'SOE', 'Prof. Sarah Mitchell', 'Excellence in civil, mechanical, and electrical engineering programs', 2003, 1),
('School of Business', 'SOB', 'Dr. Robert Thompson', 'Comprehensive business education with focus on management and commerce', 2008, 1),
('School of Health Sciences', 'SOHS', 'Dr. Emily Davis', 'Medical, nursing, and public health programs', 2010, 1),
('School of Natural Sciences', 'SONS', 'Prof. James Wilson', 'Mathematics, physics, chemistry, and biology programs', 2004, 1);

-- Departments
INSERT INTO departments (department_name, department_code, school_id, hod_name, description, is_active) VALUES
-- Computing Departments
('Computer Science', 'CS', 1, 'Dr. Alan Turing', 'Software development, algorithms, and computational theory', 1),
('Information Technology', 'IT', 1, 'Dr. Grace Hopper', 'Network administration, cybersecurity, and IT management', 1),
('Software Engineering', 'SE', 1, 'Dr. Linus Torvalds', 'Software design, development methodologies, and quality assurance', 1),

-- Engineering Departments
('Civil Engineering', 'CE', 2, 'Dr. Isambard Kingdom', 'Infrastructure, construction, and structural engineering', 1),
('Mechanical Engineering', 'ME', 2, 'Dr. James Watt', 'Machine design, thermodynamics, and manufacturing', 1),
('Electrical Engineering', 'EE', 2, 'Dr. Nikola Tesla', 'Electronics, power systems, and telecommunications', 1),

-- Business Departments
('Business Administration', 'BA', 3, 'Dr. Peter Drucker', 'Management, marketing, and organizational behavior', 1),
('Commerce', 'COM', 3, 'Dr. Adam Smith', 'Accounting, finance, and business law', 1),

-- Health Sciences Departments
('Nursing', 'NUR', 4, 'Dr. Florence Nightingale', 'Clinical nursing and healthcare management', 1),
('Public Health', 'PH', 4, 'Dr. John Snow', 'Epidemiology, health policy, and community health', 1),

-- Natural Sciences Departments
('Mathematics', 'MAT', 5, 'Dr. Isaac Newton', 'Pure and applied mathematics', 1),
('Physics', 'PHY', 5, 'Dr. Albert Einstein', 'Classical and modern physics', 1);

-- Programmes
INSERT INTO programmes (programme_name, programme_code, department_id, description, duration_years, degree_level, is_active) VALUES
-- Computing Programmes
('Bachelor of Science in Computer Science', 'BSC-CS', 1, 'Comprehensive computer science education covering algorithms, software development, and computational theory', 4, 'bachelor', 1),
('Bachelor of Science in Information Technology', 'BSC-IT', 2, 'IT management, network administration, and information systems', 4, 'bachelor', 1),
('Bachelor of Science in Software Engineering', 'BSC-SE', 3, 'Software design, development, testing, and project management', 4, 'bachelor', 1),

-- Engineering Programmes
('Bachelor of Engineering in Civil Engineering', 'BENG-CE', 4, 'Civil engineering design, construction, and infrastructure management', 5, 'bachelor', 1),
('Bachelor of Engineering in Mechanical Engineering', 'BENG-ME', 5, 'Mechanical systems design, thermodynamics, and manufacturing processes', 5, 'bachelor', 1),
('Bachelor of Engineering in Electrical Engineering', 'BENG-EE', 6, 'Electrical systems, electronics, and power engineering', 5, 'bachelor', 1),

-- Business Programmes
('Bachelor of Business Administration', 'BBA', 7, 'Business management, marketing, human resources, and entrepreneurship', 4, 'bachelor', 1),
('Bachelor of Commerce', 'BCOM', 8, 'Accounting, finance, banking, and business law', 4, 'bachelor', 1),

-- Health Sciences Programmes
('Bachelor of Science in Nursing', 'BSC-NUR', 9, 'Clinical nursing, patient care, and healthcare management', 4, 'bachelor', 1),
('Bachelor of Science in Public Health', 'BSC-PH', 10, 'Epidemiology, health policy, and community health programs', 4, 'bachelor', 1),

-- Natural Sciences Programmes
('Bachelor of Science in Mathematics', 'BSC-MAT', 11, 'Pure mathematics, applied mathematics, and statistics', 4, 'bachelor', 1),
('Bachelor of Science in Physics', 'BSC-PHY', 12, 'Classical physics, quantum mechanics, and astrophysics', 4, 'bachelor', 1);

-- ============================================================
-- 3. ACADEMIC CALENDAR
-- ============================================================

-- Academic Session
INSERT INTO academic_sessions (session_name, academic_year, start_date, end_date, is_current) VALUES
('2026/2027 Academic Session', '2026/2027', '2026-09-01', '2027-06-30', 1);

-- Semesters
INSERT INTO semesters (semester_name, semester_number, session_id, start_date, end_date, registration_start, registration_deadline, is_active, is_registration_open) VALUES
('Semester 1 - 2026/2027', 1, 1, '2026-09-01', '2026-12-20', '2026-08-15', '2026-09-15', 1, 1),
('Semester 2 - 2026/2027', 2, 1, '2027-01-10', '2027-04-30', '2027-01-01', '2027-01-20', 0, 0);

-- ============================================================
-- 4. STAFF MEMBERS
-- ============================================================

-- Admins
INSERT INTO admins (user_id, admin_name, staff_id, role_level, department_id, is_active) VALUES
(1, 'System Administrator', 'ADM001', 'super_admin', NULL, 1),
(2, 'Registrar Johnson', 'ADM002', 'registrar', NULL, 1);

-- Lecturers
INSERT INTO lecturers (user_id, lecturer_name, staff_id, department_id, email, phone, title, qualification, specialization, is_active) VALUES
(6, 'Dr. Robert Johnson', 'LEC001', 1, 'dr.johnson@university.edu', '+254712345678', 'Senior Lecturer', 'PhD in Computer Science', 'Artificial Intelligence and Machine Learning', 1),
(7, 'Prof. Mary Williams', 'LEC002', 1, 'prof.williams@university.edu', '+254712345679', 'Professor', 'PhD in Software Engineering', 'Distributed Systems and Cloud Computing', 1);

-- Additional lecturers without user accounts (can be linked later)
INSERT INTO lecturers (lecturer_name, staff_id, department_id, email, phone, title, qualification, specialization, is_active) VALUES
('Dr. James Brown', 'LEC003', 2, 'dr.brown@university.edu', '+254712345680', 'Lecturer', 'PhD in Information Technology', 'Network Security and Cryptography', 1),
('Dr. Patricia Davis', 'LEC004', 4, 'dr.davis@university.edu', '+254712345681', 'Senior Lecturer', 'PhD in Civil Engineering', 'Structural Engineering', 1),
('Prof. Michael Miller', 'LEC005', 7, 'prof.miller@university.edu', '+254712345682', 'Professor', 'PhD in Business Administration', 'Strategic Management', 1);

-- ============================================================
-- 5. SAMPLE STUDENTS
-- ============================================================

INSERT INTO students (user_id, registration_number, student_name, phone, date_of_birth, gender, id_number, department_id, programme_id, year_of_study, entry_year, status) VALUES
(3, 'CS/2026/0001', 'John Doe', '+254722111222', '2003-05-15', 'male', '12345678', 1, 1, 1, 2026, 'active'),
(4, 'IT/2026/0002', 'Jane Smith', '+254733222333', '2003-08-20', 'female', '23456789', 2, 2, 1, 2026, 'active'),
(5, NULL, 'David Wilson', '+254744333444', '2004-03-10', 'male', '34567890', NULL, NULL, 1, 2026, 'active');

-- ============================================================
-- 6. COMPUTER SCIENCE PROGRAMME UNITS
-- ============================================================

-- Year 1, Semester 1 Units
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('CS101', 'Introduction to Programming', 4, 1, 1, 1, 1, 0, 'Fundamentals of programming using Python and Java - variables, control structures, functions, and OOP basics'),
('CS102', 'Discrete Mathematics', 3, 1, 1, 1, 1, 0, 'Mathematical foundations for computer science - logic, sets, relations, functions, and proof techniques'),
('CS103', 'Computer Organization and Architecture', 4, 1, 2, 1, 1, 0, 'Computer hardware architecture, assembly language, and system organization'),
('CS104', 'Introduction to Algorithms', 3, 1, 1, 1, 1, 0, 'Algorithm design, analysis, and complexity - sorting, searching, and basic data structures'),
('CS105', 'Web Development Fundamentals', 3, 1, 2, 1, 1, 0, 'HTML5, CSS3, JavaScript, responsive design, and modern web technologies'),
('CS106', 'Professional Communication', 2, 1, NULL, 1, 1, 0, 'Technical writing, presentation skills, and professional ethics in computing');

-- Year 1, Semester 2 Units
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('CS111', 'Object-Oriented Programming', 4, 1, 1, 2, 1, 0, 'OOP principles using Java and C++ - inheritance, polymorphism, encapsulation, and design patterns'),
('CS112', 'Data Structures and Algorithms', 4, 1, 1, 2, 1, 0, 'Advanced data structures - arrays, linked lists, stacks, queues, trees, graphs, and hash tables'),
('CS113', 'Database Systems', 4, 1, 2, 2, 1, 0, 'Relational database design, SQL, normalization, and database management'),
('CS114', 'Computer Networks', 3, 1, 2, 2, 1, 0, 'Network protocols, TCP/IP, OSI model, and network architecture'),
('CS115', 'Operating Systems', 4, 1, 1, 2, 1, 0, 'OS concepts - process management, memory management, file systems, and concurrency'),
('CS116', 'Linear Algebra', 3, 1, NULL, 2, 1, 0, 'Vectors, matrices, eigenvalues, and linear transformations for computer graphics and ML');

-- Year 2, Semester 1 Units (Advanced Topics)
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('CS201', 'Systems Programming', 4, 1, 2, 1, 2, 0, 'Low-level programming, system calls, concurrent programming, and inter-process communication'),
('CS202', 'Distributed Systems', 4, 1, 2, 1, 2, 0, 'Distributed computing, consensus algorithms, microservices, and cloud architectures'),
('CS203', 'Artificial Intelligence', 4, 1, 1, 1, 2, 0, 'AI fundamentals, search algorithms, machine learning, and neural networks'),
('CS204', 'Theory of Computation', 3, 1, 1, 1, 2, 0, 'Finite automata, formal languages, Turing machines, and computability theory'),
('CS205', 'Software Engineering', 4, 1, 2, 1, 2, 0, 'SDLC, agile methodologies, testing, version control, and project management'),
('CS206', 'Computer Graphics', 3, 1, 1, 1, 2, 0, '2D/3D graphics, rendering algorithms, animation, and visualization techniques');

-- ============================================================
-- 7. INFORMATION TECHNOLOGY PROGRAMME UNITS
-- ============================================================

-- Year 1, Semester 1
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('IT101', 'Introduction to Information Technology', 3, 2, 3, 1, 1, 0, 'IT fundamentals, hardware, software, and information systems'),
('IT102', 'Network Fundamentals', 4, 2, 3, 1, 1, 0, 'Networking basics, protocols, IP addressing, and LAN/WAN concepts'),
('IT103', 'Programming Basics', 3, 2, 3, 1, 1, 0, 'Introduction to programming using Python'),
('IT104', 'Database Fundamentals', 4, 2, NULL, 1, 1, 0, 'Database concepts, SQL, and basic database design'),
('IT105', 'Web Technologies', 3, 2, NULL, 1, 1, 0, 'HTML, CSS, JavaScript, and web development basics'),
('IT106', 'IT Professional Skills', 2, 2, NULL, 1, 1, 0, 'Communication, teamwork, and IT ethics');

-- Year 1, Semester 2
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('IT111', 'Advanced Networking', 4, 2, 3, 2, 1, 0, 'Routing, switching, network security, and troubleshooting'),
('IT112', 'System Administration', 4, 2, 3, 2, 1, 0, 'Windows and Linux server administration'),
('IT113', 'Cybersecurity Basics', 4, 2, 3, 2, 1, 0, 'Information security principles, threats, and protection mechanisms'),
('IT114', 'IT Project Management', 3, 2, NULL, 2, 1, 0, 'Project planning, execution, and management in IT context'),
('IT115', 'Cloud Computing', 3, 2, NULL, 2, 1, 0, 'Cloud platforms, services (IaaS, PaaS, SaaS), and deployment'),
('IT116', 'Mobile Application Development', 3, 2, NULL, 2, 1, 0, 'Mobile app development for Android and iOS');

-- ============================================================
-- 8. SOFTWARE ENGINEERING PROGRAMME UNITS
-- ============================================================

-- Year 1, Semester 1
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('SE101', 'Introduction to Software Engineering', 3, 3, 2, 1, 1, 0, 'Software development lifecycle, methodologies, and best practices'),
('SE102', 'Programming Fundamentals', 4, 3, 2, 1, 1, 0, 'Programming using Java - syntax, control structures, and OOP'),
('SE103', 'Data Structures', 4, 3, NULL, 1, 1, 0, 'Arrays, linked lists, stacks, queues, trees, and graphs'),
('SE104', 'Discrete Mathematics for SE', 3, 3, NULL, 1, 1, 0, 'Logic, sets, combinatorics, and graph theory'),
('SE105', 'Requirements Engineering', 3, 3, 2, 1, 1, 0, 'Requirements gathering, analysis, and specification'),
('SE106', 'Professional Communication', 2, 3, NULL, 1, 1, 0, 'Technical writing and presentation skills');

-- Year 1, Semester 2
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('SE111', 'Object-Oriented Analysis and Design', 4, 3, 2, 2, 1, 0, 'UML, design patterns, and OO principles'),
('SE112', 'Software Testing and QA', 4, 3, 2, 2, 1, 0, 'Testing methodologies, test automation, and quality assurance'),
('SE113', 'Database Design and Implementation', 4, 3, NULL, 2, 1, 0, 'Advanced database design, SQL, and database optimization'),
('SE114', 'Web Application Development', 4, 3, NULL, 2, 1, 0, 'Full-stack web development using modern frameworks'),
('SE115', 'Algorithms and Complexity', 3, 3, NULL, 2, 1, 0, 'Algorithm design, analysis, and computational complexity'),
('SE116', 'Version Control and DevOps', 3, 3, NULL, 2, 1, 0, 'Git, CI/CD pipelines, and modern DevOps practices');

-- ============================================================
-- 9. CIVIL ENGINEERING PROGRAMME UNITS
-- ============================================================

-- Year 1, Semester 1
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('CE101', 'Engineering Mathematics I', 4, 4, NULL, 1, 1, 0, 'Calculus, differential equations for engineering'),
('CE102', 'Engineering Drawing', 3, 4, 4, 1, 1, 0, 'Technical drawing, CAD, and visualization'),
('CE103', 'Mechanics of Materials', 4, 4, 4, 1, 1, 0, 'Stress, strain, and material properties'),
('CE104', 'Surveying I', 4, 4, 4, 1, 1, 0, 'Land surveying techniques and instruments'),
('CE105', 'Engineering Physics', 3, 4, NULL, 1, 1, 0, 'Physics principles for engineering applications'),
('CE106', 'Computer Applications in Engineering', 3, 4, NULL, 1, 1, 0, 'Software tools for civil engineering');

-- Year 1, Semester 2
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('CE111', 'Engineering Mathematics II', 4, 4, NULL, 2, 1, 0, 'Advanced calculus and linear algebra'),
('CE112', 'Structural Analysis I', 4, 4, 4, 2, 1, 0, 'Analysis of structures, beams, and frames'),
('CE113', 'Fluid Mechanics', 4, 4, 4, 2, 1, 0, 'Fluid properties, flow, and hydraulics'),
('CE114', 'Construction Materials', 3, 4, 4, 2, 1, 0, 'Properties and testing of construction materials'),
('CE115', 'Geotechnical Engineering I', 4, 4, NULL, 2, 1, 0, 'Soil mechanics and foundation engineering'),
('CE116', 'Engineering Communication', 2, 4, NULL, 2, 1, 0, 'Technical report writing and presentation');

-- ============================================================
-- 10. BUSINESS ADMINISTRATION PROGRAMME UNITS
-- ============================================================

-- Year 1, Semester 1
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('BA101', 'Principles of Management', 3, 7, 5, 1, 1, 0, 'Management theories, functions, and organizational behavior'),
('BA102', 'Financial Accounting', 4, 7, NULL, 1, 1, 0, 'Accounting principles, financial statements, and analysis'),
('BA103', 'Business Mathematics', 3, 7, NULL, 1, 1, 0, 'Mathematical concepts for business applications'),
('BA104', 'Microeconomics', 4, 7, 5, 1, 1, 0, 'Consumer behavior, market structures, and resource allocation'),
('BA105', 'Business Communication', 3, 7, NULL, 1, 1, 0, 'Professional communication in business context'),
('BA106', 'Introduction to Business Law', 3, 7, NULL, 1, 1, 0, 'Legal framework for business operations');

-- Year 1, Semester 2
INSERT INTO units (unit_code, unit_name, credit_hours, programme_id, lecturer_id, semester_number, year_of_study, is_elective, description) VALUES
('BA111', 'Marketing Principles', 4, 7, 5, 2, 1, 0, 'Marketing concepts, strategies, and consumer behavior'),
('BA112', 'Organizational Behavior', 4, 7, 5, 2, 1, 0, 'Individual and group behavior in organizations'),
('BA113', 'Macroeconomics', 4, 7, NULL, 2, 1, 0, 'National income, inflation, unemployment, and fiscal policy'),
('BA114', 'Business Statistics', 3, 7, NULL, 2, 1, 0, 'Statistical methods for business decision making'),
('BA115', 'Human Resource Management', 3, 7, NULL, 2, 1, 0, 'HRM practices, recruitment, and employee relations'),
('BA116', 'Entrepreneurship', 3, 7, 5, 2, 1, 0, 'Starting and managing a business venture');

-- ============================================================
-- 11. SAMPLE KCSE INFORMATION
-- ============================================================

INSERT INTO kcse_info (student_id, kcse_year, index_number, school_name, mean_grade, points) VALUES
(1, 2025, '12345678', 'Nairobi High School', 'B+', 10),
(2, 2025, '23456789', 'Mombasa Girls School', 'A-', 11);

INSERT INTO kcse_grades (student_id, subject, grade, points) VALUES
-- John Doe's KCSE Results
(1, 'Mathematics', 'A', 12),
(1, 'English', 'B+', 11),
(1, 'Kiswahili', 'B', 10),
(1, 'Physics', 'A-', 11),
(1, 'Chemistry', 'B+', 11),
(1, 'Biology', 'B', 10),
(1, 'Computer Studies', 'A', 12),
(1, 'History', 'B', 10),

-- Jane Smith's KCSE Results
(2, 'Mathematics', 'A-', 11),
(2, 'English', 'A', 12),
(2, 'Kiswahili', 'B+', 11),
(2, 'Physics', 'A', 12),
(2, 'Chemistry', 'A-', 11),
(2, 'Biology', 'A', 12),
(2, 'Computer Studies', 'A', 12),
(2, 'Geography', 'B+', 11);

-- ============================================================
-- 12. SAMPLE APPLICATIONS
-- ============================================================

INSERT INTO applications (student_id, programme_id, status, priority, applied_at, reviewed_at, approved_by, remarks) VALUES
(1, 1, 'approved', 1, '2026-08-01 10:00:00', '2026-08-05 14:30:00', 1, 'Excellent academic record. Approved for Computer Science.'),
(2, 2, 'approved', 1, '2026-08-02 11:00:00', '2026-08-06 15:00:00', 1, 'Strong IT background. Approved for Information Technology.'),
(3, 3, 'pending', 1, '2026-08-03 09:00:00', NULL, NULL, 'Application under review.');

-- ============================================================
-- 13. SAMPLE REGISTRATIONS
-- ============================================================

-- John Doe's registrations for Semester 1
INSERT INTO registrations (student_id, unit_id, semester_id, registration_date, status, approved_by, approved_at) VALUES
(1, 1, 1, '2026-08-20 10:00:00', 'approved', 1, '2026-08-21 09:00:00'),
(1, 2, 1, '2026-08-20 10:00:00', 'approved', 1, '2026-08-21 09:00:00'),
(1, 3, 1, '2026-08-20 10:00:00', 'approved', 1, '2026-08-21 09:00:00'),
(1, 4, 1, '2026-08-20 10:00:00', 'approved', 1, '2026-08-21 09:00:00'),
(1, 5, 1, '2026-08-20 10:00:00', 'approved', 1, '2026-08-21 09:00:00'),
(1, 6, 1, '2026-08-20 10:00:00', 'approved', 1, '2026-08-21 09:00:00');

-- Jane Smith's registrations for Semester 1
INSERT INTO registrations (student_id, unit_id, semester_id, registration_date, status, approved_by, approved_at) VALUES
(2, 7, 1, '2026-08-22 11:00:00', 'approved', 1, '2026-08-23 10:00:00'),
(2, 8, 1, '2026-08-22 11:00:00', 'approved', 1, '2026-08-23 10:00:00'),
(2, 9, 1, '2026-08-22 11:00:00', 'approved', 1, '2026-08-23 10:00:00'),
(2, 10, 1, '2026-08-22 11:00:00', 'approved', 1, '2026-08-23 10:00:00'),
(2, 11, 1, '2026-08-22 11:00:00', 'approved', 1, '2026-08-23 10:00:00'),
(2, 12, 1, '2026-08-22 11:00:00', 'approved', 1, '2026-08-23 10:00:00');

-- ============================================================
-- 14. SAMPLE RESULTS
-- ============================================================

-- John Doe's results for Year 1, Semester 1
INSERT INTO results (student_id, unit_id, semester_id, cat_marks, exam_marks, total_marks, grade, grade_points, is_published) VALUES
(1, 1, 1, 28, 65, 93, 'A', 4.00, 1),
(1, 2, 1, 25, 58, 83, 'A-', 3.70, 1),
(1, 3, 1, 27, 60, 87, 'A-', 3.70, 1),
(1, 4, 1, 29, 66, 95, 'A', 4.00, 1),
(1, 5, 1, 26, 62, 88, 'A-', 3.70, 1),
(1, 6, 1, 24, 56, 80, 'B+', 3.30, 1);

-- Jane Smith's results for Year 1, Semester 1
INSERT INTO results (student_id, unit_id, semester_id, cat_marks, exam_marks, total_marks, grade, grade_points, is_published) VALUES
(2, 7, 1, 27, 63, 90, 'A', 4.00, 1),
(2, 8, 1, 28, 64, 92, 'A', 4.00, 1),
(2, 9, 1, 26, 59, 85, 'A-', 3.70, 1),
(2, 10, 1, 25, 57, 82, 'A-', 3.70, 1),
(2, 11, 1, 29, 67, 96, 'A', 4.00, 1),
(2, 12, 1, 27, 61, 88, 'A-', 3.70, 1);

-- ============================================================
-- 15. SAMPLE TIMETABLES
-- ============================================================

-- Computer Science Units Timetable
INSERT INTO timetables (unit_id, semester_id, day_of_week, start_time, end_time, venue, session_type) VALUES
(1, 1, 'Monday', '08:00:00', '10:00:00', 'Lab A101', 'lecture'),
(2, 1, 'Monday', '10:00:00', '12:00:00', 'LH 201', 'lecture'),
(3, 1, 'Tuesday', '08:00:00', '10:00:00', 'LH 203', 'lecture'),
(4, 1, 'Tuesday', '10:00:00', '12:00:00', 'LH 205', 'lecture'),
(5, 1, 'Wednesday', '08:00:00', '10:00:00', 'Lab A102', 'practical'),
(6, 1, 'Wednesday', '10:00:00', '12:00:00', 'LH 207', 'lecture');

-- Information Technology Units Timetable
INSERT INTO timetables (unit_id, semester_id, day_of_week, start_time, end_time, venue, session_type) VALUES
(7, 1, 'Monday', '14:00:00', '16:00:00', 'LH 301', 'lecture'),
(8, 1, 'Tuesday', '14:00:00', '16:00:00', 'Lab B101', 'practical'),
(9, 1, 'Wednesday', '14:00:00', '16:00:00', 'LH 303', 'lecture'),
(10, 1, 'Thursday', '08:00:00', '10:00:00', 'LH 305', 'lecture'),
(11, 1, 'Thursday', '10:00:00', '12:00:00', 'Lab B102', 'practical'),
(12, 1, 'Friday', '08:00:00', '10:00:00', 'LH 307', 'lecture');

-- ============================================================
-- 16. SAMPLE ANNOUNCEMENTS
-- ============================================================

INSERT INTO announcements (title, message, target_audience, priority, posted_by, is_published, date_posted, expiry_date) VALUES
('Welcome to 2026/2027 Academic Session', 'We welcome all students to the new academic year. Registration is now open.', 'all', 'high', 1, 1, '2026-08-15 09:00:00', '2026-09-15 23:59:59'),
('Registration Deadline Reminder', 'Reminder: Course registration closes on September 15, 2026. Ensure you complete your registration.', 'students', 'urgent', 1, 1, '2026-09-01 08:00:00', '2026-09-15 23:59:59'),
('Library Hours Extended', 'The university library will remain open until 10 PM during the examination period.', 'all', 'normal', 1, 1, '2026-11-01 10:00:00', '2026-12-20 23:59:59'),
('Mid-Semester Exams Schedule', 'Mid-semester exams will be held from October 15-20, 2026. Check your timetable for details.', 'students', 'high', 1, 1, '2026-10-01 09:00:00', '2026-10-20 23:59:59');

-- ============================================================
-- 17. SAMPLE NOTIFICATIONS
-- ============================================================

INSERT INTO notifications (user_id, title, message, type, is_read, action_url) VALUES
(3, 'Welcome to the University', 'Your account has been created successfully. Please complete your academic information.', 'info', 0, '/admission/academic-info'),
(3, 'Application Submitted', 'Your programme application has been submitted and is under review.', 'success', 0, '/admission/status'),
(4, 'Application Approved', 'Congratulations! Your application has been approved. Your registration number is IT/2026/0002', 'success', 1, '/student/dashboard'),
(5, 'Registration Successful', 'Your course registration has been approved. View your units on your dashboard.', 'success', 0, '/student/my-units');

-- ============================================================
-- 18. SYSTEM SETTINGS
-- ============================================================

INSERT INTO system_settings (setting_key, setting_value, description, is_public) VALUES
('university_name', 'University of Excellence', 'The official name of the institution', 1),
('registration_open', 'true', 'Global flag to enable/disable course registration', 0),
('max_credit_hours', '24', 'Maximum credit hours allowed per semester', 0),
('min_credit_hours', '12', 'Minimum credit hours required per semester', 0),
('current_academic_year', '2026/2027', 'Current academic year', 1),
('admin_email', 'admin@university.edu', 'Contact email for system administrators', 1);

-- ============================================================
-- SUCCESS MESSAGE
-- ============================================================
SELECT 'University Course Registration System - Production Seed Data Loaded Successfully!' AS status,
       'Database populated with schools, departments, programmes, units, students, and sample data' AS details,
       'You can now run the application and test all features' AS next_step;