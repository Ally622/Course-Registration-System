# Demo Data Guide - Course Registration System

## Overview
The system comes with **comprehensive demo data** that allows you to test all features immediately without manual data entry.

---

## What's Included in Demo Data?

### 1. **User Accounts (Ready to Login)**

#### Admin Accounts
| Email | Password | Role |
|-------|----------|------|
| `admin@university.edu` | `admin123` | Super Admin |
| `registrar@university.edu` | `admin123` | Registrar |

#### Student Accounts
| Email | Student ID | Password | Programme |
|-------|-----------|----------|-----------|
| `john.doe@student.edu` | `CS/2026/0001` | `student123` | Computer Science |
| `jane.smith@student.edu` | `IT/2026/0002` | `student123` | Information Technology |
| `david.wilson@student.edu` | N/A | `student123` | Pending |

#### Lecturer Accounts
| Email | Password | Department |
|-------|----------|------------|
| `dr.johnson@university.edu` | `lecturer123` | Computer Science |
| `prof.williams@university.edu` | `lecturer123` | Computer Science |

---

### 2. **Academic Structure**

#### Schools (5)
- School of Computing and Information Technology (SCIT)
- School of Engineering (SOE)
- School of Business (SOB)
- School of Health Sciences (SOHS)
- School of Natural Sciences (SONS)

#### Departments (12)
- Computer Science, IT, Software Engineering
- Civil Engineering, Mechanical Engineering, Electrical Engineering
- Business Administration, Commerce
- Nursing, Public Health
- Mathematics, Physics

#### Programmes (12)
- **Computing**: BSc Computer Science, BSc IT, BSc Software Engineering
- **Engineering**: BEng Civil, BEng Mechanical, BEng Electrical
- **Business**: BBA, BCom
- **Health**: BSc Nursing, BSc Public Health
- **Sciences**: BSc Mathematics, BSc Physics

---

### 3. **Course Units (100+)**

#### Computer Science Programme
**Year 1, Semester 1** (Currently Active):
- CS101 - Introduction to Programming (4 credits)
- CS102 - Discrete Mathematics (3 credits)
- CS103 - Computer Organization and Architecture (4 credits)
- CS104 - Introduction to Algorithms (3 credits)
- CS105 - Web Development Fundamentals (3 credits)
- CS106 - Professional Communication (2 credits)

**Year 1, Semester 2**:
- CS111 - Object-Oriented Programming (4 credits)
- CS112 - Data Structures and Algorithms (4 credits)
- CS113 - Database Systems (4 credits)
- CS114 - Computer Networks (3 credits)
- CS115 - Operating Systems (4 credits)
- CS116 - Linear Algebra (3 credits)

**Year 2, Semester 1**:
- CS201 - Systems Programming
- CS202 - Distributed Systems
- CS203 - Artificial Intelligence
- CS204 - Theory of Computation
- CS205 - Software Engineering
- CS206 - Computer Graphics

#### Information Technology Programme
**Year 1, Semester 1** (Currently Active):
- IT101 - Introduction to Information Technology
- IT102 - Network Fundamentals
- IT103 - Programming Basics
- IT104 - Database Fundamentals
- IT105 - Web Technologies
- IT106 - IT Professional Skills

**Year 1, Semester 2**:
- IT111 - Advanced Networking
- IT112 - System Administration
- IT113 - Cybersecurity Basics
- IT114 - IT Project Management
- IT115 - Cloud Computing
- IT116 - Mobile Application Development

#### Software Engineering, Civil Engineering, Business Administration
...and many more! **100+ course units** across all programmes.

---

### 4. **Academic Calendar**

#### Current Session: **2026/2027**
- **Start**: September 1, 2026
- **End**: June 30, 2027

#### Semesters:
1. **Semester 1** (ACTIVE)
   - Duration: Sep 1 - Dec 20, 2026
   - Registration: Aug 15 - Sep 15, 2026
   - Status: ✅ **Registration OPEN**

2. **Semester 2**
   - Duration: Jan 10 - Apr 30, 2027
   - Registration: Jan 1 - Jan 20, 2027
   - Status: Inactive

---

### 5. **Sample Registrations**

#### John Doe (CS/2026/0001) - Already Registered
- CS101 - Introduction to Programming ✅
- CS102 - Discrete Mathematics ✅
- CS103 - Computer Organization and Architecture ✅
- CS104 - Introduction to Algorithms ✅
- CS105 - Web Development Fundamentals ✅
- CS106 - Professional Communication ✅
- **Total**: 19 credits

#### Jane Smith (IT/2026/0002) - Already Registered
- IT101 - Introduction to Information Technology ✅
- IT102 - Network Fundamentals ✅
- IT103 - Programming Basics ✅
- IT104 - Database Fundamentals ✅
- IT105 - Web Technologies ✅
- IT106 - IT Professional Skills ✅
- **Total**: 19 credits

---

### 6. **Sample Results**

Both John and Jane have **published results** for Semester 1:

**John Doe's Results**:
- CS101: 93 marks, Grade A
- CS102: 83 marks, Grade A-
- CS103: 87 marks, Grade A-
- CS104: 95 marks, Grade A
- CS105: 88 marks, Grade A-
- CS106: 80 marks, Grade B+
- **GPA**: 3.73

**Jane Smith's Results**:
- IT101-IT106: All A and A- grades
- **GPA**: 3.87

---

### 7. **Timetables**

Complete timetables for:
- Computer Science units (Mon-Wed)
- Information Technology units (Mon-Fri)
- All other programmes

---

### 8. **Additional Data**

- ✅ **Announcements**: Welcome messages, reminders
- ✅ **Notifications**: System notifications for students
- ✅ **KCSE Records**: Sample high school results
- ✅ **Applications**: Sample programme applications
- ✅ **System Settings**: Configured and ready

---

## How to Load Demo Data

### Method 1: Using the Batch Script (Easiest)
1. Open folder in File Explorer
2. Double-click `load_demo_data.bat`
3. Enter MySQL password when prompted
4. Wait for success message

### Method 2: Manual MySQL Command
```bash
# Navigate to project directory
cd "C:\Users\CHEMOGET\Desktop\3.1\software engineering\COURSE_REGISTRATION_SYSTEM\Course_Registration"

# Load schema (if not already loaded)
mysql -u root -p course_registration_system < database/schema.sql

# Load demo data
mysql -u root -p course_registration_system < database/seed_data.sql
```

### Method 3: MySQL Workbench
1. Open MySQL Workbench
2. Connect to your database
3. Open `database/schema.sql` and execute
4. Open `database/seed_data.sql` and execute

---

## Testing the Demo Data

### As Student (John Doe):
1. Login: `john.doe@student.edu` / `student123`
2. View Dashboard → Should see stats
3. Navigate to "Course Registration" → Should see all CS courses
4. Navigate to "My Courses" → Should see 6 registered courses
5. Navigate to "Results" → Should see published results
6. Navigate to "Timetable" → Should see class schedule

### As Admin:
1. Login: `admin@university.edu` / `admin123`
2. View all students
3. See pending registrations
4. Manage courses
5. View system logs

### As New Student:
1. Register new account
2. Complete admission process
3. Select programme
4. Register for courses
5. View registered courses

---

## Data Summary

| Item | Count |
|------|-------|
| **Schools** | 5 |
| **Departments** | 12 |
| **Programmes** | 12 |
| **Course Units** | 100+ |
| **Lecturers** | 5 |
| **Students** | 3 |
| **Admin** | 2 |
| **Registrations** | 12 |
| **Results** | 12 |
| **Announcements** | 4 |
| **Timetable Entries** | 12 |

---

## Verifying Data Was Loaded

Run this Python script to verify:

```python
# verify_demo_data.py
import mysql.connector
from config import Config

try:
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    
    # Check key tables
    checks = {
        'Schools': 'SELECT COUNT(*) as count FROM schools',
        'Programmes': 'SELECT COUNT(*) as count FROM programmes',
        'Course Units': 'SELECT COUNT(*) as count FROM units',
        'Students': 'SELECT COUNT(*) as count FROM students',
        'Lecturers': 'SELECT COUNT(*) as count FROM lecturers',
        'Registrations': 'SELECT COUNT(*) as count FROM registrations'
    }
    
    print("\n=== DEMO DATA VERIFICATION ===\n")
    
    for name, query in checks.items():
        cursor.execute(query)
        count = cursor.fetchone()['count']
        status = "✅" if count > 0 else "❌"
        print(f"{status} {name}: {count}")
    
    print("\n" + "="*30 + "\n")
    
    cursor.close()
    conn.close()
    
    print("✅ Demo data is loaded and ready!\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease run load_demo_data.bat to load demo data.\n")
```

---

## Troubleshooting

### Issue: "Table doesn't exist"
**Solution**: Load schema first
```bash
mysql -u root -p course_registration_system < database/schema.sql
```

### Issue: "Duplicate entry"
**Solution**: Demo data already loaded. If you want to reload:
```sql
DROP DATABASE course_registration_system;
CREATE DATABASE course_registration_system;
-- Then run load_demo_data.bat
```

### Issue: No courses showing
**Solution**: 
1. Check you're logged in as correct user
2. Verify user has programme assigned
3. Check semester is active and registration is open

---

## Customizing Demo Data

Want to add your own data?

1. **Edit** `database/seed_data.sql`
2. **Add** your schools, programmes, courses
3. **Reload** using `load_demo_data.bat`

---

## Production Use

**Before going to production:**
1. ❌ **DO NOT use demo passwords** (`admin123`, `student123`)
2. ✅ Change all default passwords
3. ✅ Remove test accounts
4. ✅ Add your real academic structure
5. ✅ Update system settings

---

## Quick Reference

### Test Credentials
```
ADMIN:    admin@university.edu / admin123
STUDENT:  john.doe@student.edu / student123
          OR CS/2026/0001 / student123
LECTURER: dr.johnson@university.edu / lecturer123
```

### Key Facts
- **Current Semester**: 1 (2026/2027)
- **Registration Status**: ✅ OPEN
- **Registration Deadline**: September 15, 2026
- **Total Courses Available**: 100+
- **Max Credits/Semester**: 24

---

**Status**: ✅ **Demo Data Ready - Start Testing Now!**

Run `python app.py` and login with any of the test accounts above.
