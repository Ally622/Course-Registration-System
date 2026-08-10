# Database Documentation

## Overview

The University Course Registration System uses a MySQL database with a normalized structure supporting the complete academic workflow from student admission to course completion.

## Database Structure

### Core Hierarchy
```
Schools
├── Departments
    ├── Programmes (Degree Programs)
        ├── Units (Individual Subjects)
            ├── Registrations (Student Enrollments)
            ├── Results (Academic Performance)
            └── Timetables (Class Schedules)
```

### Key Relationships

1. **Academic Structure**:
   - Schools contain multiple Departments
   - Departments offer multiple Programmes
   - Programmes contain multiple Units per semester
   - Units have Prerequisites relationships

2. **Student Management**:
   - Students belong to one Programme
   - Students register for Units within their Programme
   - Results track performance per Unit per Semester
   - Applications manage the admission process

3. **Administrative Control**:
   - Admins approve Applications and Registrations
   - Lecturers are assigned to Units
   - Semesters control academic periods

## Files

### Core Files
- **`schema.sql`**: Complete database structure definition
- **`seed_data.sql`**: Initial data for testing and development

### Migration Files (Historical)
- **`migrations/001_auth_flow.sql`**: Authentication system setup
- **`migrations/002_admission.sql`**: Admission workflow tables
- **`migrations/003_add_programme_to_units.sql`**: Programme-Unit relationships
- **`migrations/004_add_duration_years.sql`**: Programme duration configuration

## Setup Instructions

### 1. Create Database
```sql
CREATE DATABASE course_registration_system 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE course_registration_system;
```

### 2. Import Schema
```sql
SOURCE schema.sql;
```

### 3. Import Initial Data
```sql
SOURCE seed_data.sql;
```

### 4. Verify Setup
```sql
-- Check all tables exist
SHOW TABLES;

-- Verify sample data
SELECT COUNT(*) AS schools FROM schools;
SELECT COUNT(*) AS programmes FROM programmes;
SELECT COUNT(*) AS units FROM units;
```

## Table Descriptions

### Authentication & Users
- **`users`**: Base authentication table (email/password)
- **`students`**: Student-specific information and registration numbers
- **`admins`**: Administrative users with role levels
- **`lecturers`**: Faculty members assigned to units

### Academic Structure
- **`schools`**: Top-level academic divisions (e.g., School of Computing)
- **`departments`**: Departments within schools (e.g., Computer Science)
- **`programmes`**: Degree programs (e.g., BSc Computer Science)
- **`units`**: Individual subjects/courses within programmes

### Academic Operations
- **`semesters`**: Academic periods with registration deadlines
- **`applications`**: Student programme applications (admission workflow)
- **`registrations`**: Student enrollments in specific units
- **`results`**: Academic performance records
- **`timetables`**: Class schedules

### Supporting Tables
- **`kcse_info`** & **`kcse_grades`**: KCSE examination data
- **`prerequisites`**: Unit prerequisite relationships
- **`announcements`**: System-wide communications
- **`notifications`**: User-specific messages
- **`logs`**: System activity tracking

## Key Constraints

### Primary Keys
All tables use auto-incrementing integer primary keys (`table_name_id`).

### Foreign Key Relationships
- Strict referential integrity with cascading deletes where appropriate
- SET NULL for optional relationships (e.g., lecturers can be unassigned)
- CASCADE for dependent data (e.g., deleting a student removes their applications)

### Unique Constraints
- **Email addresses** must be unique across all users
- **Registration numbers** are unique per student
- **Unit codes** are unique system-wide
- **Student-Unit-Semester** combinations prevent duplicate registrations

### Data Integrity Rules
1. Students can only be assigned to one programme at a time
2. Units must belong to a programme
3. Registrations must reference valid student-unit-semester combinations
4. Results require corresponding registrations
5. Only active semesters allow new registrations

## Indexes

Performance indexes are created on frequently queried columns:
- User email lookups
- Student registration numbers
- Programme and unit associations
- Registration status queries
- Timetable day filtering

## Sample Data

The seed data includes:
- **5 Schools** with realistic academic divisions
- **20+ Programmes** across different disciplines
- **100+ Units** with proper programme associations
- **Sample Students** with complete admission records
- **Administrative Users** for system management
- **Academic Calendar** with active semester configuration

## Migration History

### Version 1.0: Initial Structure
- Basic user authentication
- Student and admin roles
- Simple course structure

### Version 2.0: Enhanced Admission
- KCSE information tracking
- Application workflow
- Programme selection process

### Version 3.0: Programme-Unit Refactoring
- Clear separation of programmes and units
- Enhanced academic structure
- Automatic unit assignment

### Version 4.0: Final Production Structure
- Complete normalization
- Performance optimization
- Comprehensive constraints

## Security Considerations

### Password Security
- All passwords are hashed using bcrypt
- No plain text passwords stored
- Password reset tokens have expiration

### Data Protection
- Foreign key constraints prevent orphaned records
- Cascading rules protect referential integrity
- Input validation prevents SQL injection

### Access Control
- Role-based permissions (student/admin/lecturer)
- Session-based authentication
- CSRF protection enabled

## Maintenance

### Backup Recommendations
```sql
-- Create backup
mysqldump -u root -p course_registration_system > backup_$(date +%Y%m%d).sql

-- Restore backup
mysql -u root -p course_registration_system < backup_file.sql
```

### Performance Monitoring
```sql
-- Check table sizes
SELECT 
    TABLE_NAME, 
    TABLE_ROWS, 
    ROUND(DATA_LENGTH/1024/1024, 2) AS 'Data Size (MB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'course_registration_system'
ORDER BY DATA_LENGTH DESC;
```

### Query Optimization
- Use EXPLAIN to analyze slow queries
- Monitor index usage
- Regular ANALYZE TABLE for statistics updates

## Troubleshooting

### Common Issues

**Foreign Key Constraint Errors**
- Check parent records exist before inserting child records
- Verify foreign key values are valid

**Duplicate Entry Errors**
- Check unique constraints on email, registration numbers, unit codes
- Use INSERT IGNORE or ON DUPLICATE KEY UPDATE where appropriate

**Connection Issues**
- Verify MySQL service is running
- Check database credentials and permissions
- Ensure database name matches configuration

### Diagnostic Queries

```sql
-- Check orphaned records
SELECT * FROM registrations r 
LEFT JOIN students s ON r.student_id = s.student_id 
WHERE s.student_id IS NULL;

-- Verify data consistency
SELECT 
    p.programme_name,
    COUNT(u.unit_id) as unit_count
FROM programmes p
LEFT JOIN units u ON p.programme_id = u.programme_id
GROUP BY p.programme_id;

-- Check active semester configuration
SELECT * FROM semesters WHERE is_active = 1;
```

---

For additional support, refer to the main project documentation or contact the development team.