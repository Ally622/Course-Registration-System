"""
Admin routes — dashboard stats, CRUD for students/courses/departments/
schools/semesters, registration approvals, analytics, and reports.

All routes are protected by @admin_required.

UPDATED (Auth Flow Refactor):
- approve_registration now generates a registration number if the student
  doesn't have one yet (format: [DEPT_PREFIX][YEAR][4-DIGIT-SEQUENCE]).
- Department CRUD includes department_prefix field.
- Admin create_student no longer requires registration_number.
"""

from datetime import datetime
from flask import request, jsonify, session

from admin import admin_bp
from db import get_connection
from auth.decorators import admin_required
from extensions import bcrypt


# =============================================================
# ADMIN DASHBOARD
# =============================================================
@admin_bp.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """
    Return summary statistics for the admin dashboard.
    Matches the Figma admin dashboard cards.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Total students
        cursor.execute("SELECT COUNT(*) AS total FROM students")
        total_students = cursor.fetchone()['total']

        # Total units
        cursor.execute("SELECT COUNT(*) AS total FROM units")
        total_units = cursor.fetchone()['total']

        # Total registrations (active semester)
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM registrations r
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            WHERE sem.is_active = 1
        """)
        total_registrations = cursor.fetchone()['total']

        # Total lecturers
        cursor.execute("SELECT COUNT(*) AS total FROM lecturers")
        total_lecturers = cursor.fetchone()['total']

        # Pending registrations
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM registrations
            WHERE status = 'pending'
        """)
        pending_registrations = cursor.fetchone()['total']

        # Pending applications
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM applications
            WHERE status = 'pending'
        """)
        pending_applications = cursor.fetchone()['total']

        # Total departments
        cursor.execute("SELECT COUNT(*) AS total FROM departments")
        total_departments = cursor.fetchone()['total']

        # Total programmes (courses)
        cursor.execute("SELECT COUNT(*) AS total FROM programmes")
        total_programmes = cursor.fetchone()['total']

        # Total schools
        cursor.execute("SELECT COUNT(*) AS total FROM schools")
        total_schools = cursor.fetchone()['total']

        # Active semester
        cursor.execute("""
            SELECT sem.semester_name, sess.academic_year, sem.is_registration_open
            FROM semesters sem
            LEFT JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE sem.is_active = 1
            LIMIT 1
        """)
        active_semester = cursor.fetchone()

        # Recent registrations
        cursor.execute("""
            SELECT
                s.student_name,
                s.registration_number,
                u.unit_code AS course_code,
                r.registration_date,
                r.status
            FROM registrations r
            INNER JOIN students s ON r.student_id = s.student_id
            INNER JOIN units u ON r.unit_id = u.unit_id
            ORDER BY r.registration_date DESC
            LIMIT 5
        """)
        recent_registrations = cursor.fetchall()

        return jsonify({
            "success": True,
            "stats": {
                "total_students": total_students,
                "total_units": total_units,
                "total_programmes": total_programmes,
                "total_registrations": total_registrations,
                "pending_registrations": pending_registrations,
                "pending_applications": pending_applications,
                "total_lecturers": total_lecturers,
                "total_departments": total_departments,
                "total_schools": total_schools
            },
            "active_semester": active_semester,
            "recent_registrations": recent_registrations
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/pending-approvals-count', methods=['GET'])
@admin_required
def pending_approvals_count():
    """Return the count of pending applications and registrations."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS count FROM registrations WHERE status = 'pending'")
        reg_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) AS count FROM applications WHERE status = 'pending'")
        app_count = cursor.fetchone()['count']
        
        return jsonify({
            "success": True, 
            "registrations_count": reg_count,
            "applications_count": app_count,
            "count": app_count # Defaulting count to applications for compatibility
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# =============================================================
# MANAGE STUDENTS — CRUD
# =============================================================
@admin_bp.route('/admin/students', methods=['GET'])
@admin_required
def list_students():
    """List all students with optional search and filter."""
    keyword = request.args.get('keyword', '').strip()
    department_id = request.args.get('department_id', '').strip()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                s.student_id,
                s.registration_number,
                s.student_name,
                s.phone,
                s.year_of_study,
                u.email,
                u.is_active,
                d.department_name
            FROM students s
            INNER JOIN users u ON s.user_id = u.user_id
            LEFT JOIN departments d ON s.department_id = d.department_id
        """

        conditions = []
        params = []

        if keyword:
            conditions.append(
                "(s.student_name LIKE %s OR s.registration_number LIKE %s OR u.email LIKE %s)"
            )
            search = f"%{keyword}%"
            params.extend([search, search, search])

        if department_id:
            conditions.append("s.department_id = %s")
            params.append(department_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY s.student_name ASC"

        cursor.execute(query, tuple(params))
        students = cursor.fetchall()

        return jsonify({"success": True, "students": students})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/students/<int:student_id>', methods=['GET'])
@admin_required
def get_student(student_id):
    """Get a single student's details."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                s.*, u.email, u.is_active,
                d.department_name, sch.school_name
            FROM students s
            INNER JOIN users u ON s.user_id = u.user_id
            LEFT JOIN departments d ON s.department_id = d.department_id
            LEFT JOIN schools sch ON d.school_id = sch.school_id
            WHERE s.student_id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({"success": False, "message": "Student not found."}), 404

        return jsonify({"success": True, "student": student})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/students', methods=['POST'])
@admin_required
def create_student():
    """Create a new student (admin action). Registration number is optional."""
    data = request.get_json()

    name = data.get("student_name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    reg_number = data.get("registration_number", "").strip() or None
    department_id = data.get("department_id")
    year_of_study = data.get("year_of_study", 1)
    password = data.get("password", "password123").strip()

    if not all([name, email]):
        return jsonify({
            "success": False,
            "message": "Name and email are required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'student')",
            (email, password_hash)
        )
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO students
                (user_id, registration_number, student_name, phone, department_id, year_of_study)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, reg_number, name, phone, department_id, year_of_study))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Student created successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    """Update a student's details."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE students
            SET student_name = %s,
                phone = %s,
                department_id = %s,
                year_of_study = %s
            WHERE student_id = %s
        """, (
            data.get("student_name"),
            data.get("phone"),
            data.get("department_id"),
            data.get("year_of_study"),
            student_id
        ))

        connection.commit()

        return jsonify({"success": True, "message": "Student updated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/students/<int:student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    """Deactivate a student (soft delete)."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT user_id FROM students WHERE student_id = %s",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            return jsonify({"success": False, "message": "Student not found."}), 404

        cursor.execute(
            "UPDATE users SET is_active = 0 WHERE user_id = %s",
            (student['user_id'],)
        )
        connection.commit()

        return jsonify({"success": True, "message": "Student deactivated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# MANAGE UNITS — CRUD
# =============================================================
@admin_bp.route('/admin/units', methods=['GET'])
@admin_required
def list_units():
    """List all units with programme and lecturer info."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                u.unit_id, u.unit_code, u.unit_name,
                u.credit_hours, u.semester_number, u.year_of_study,
                p.programme_name, l.lecturer_name
            FROM units u
            LEFT JOIN programmes p ON u.programme_id = p.programme_id
            LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
            ORDER BY u.unit_code
        """)
        units = cursor.fetchall()

        return jsonify({"success": True, "units": units})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/units', methods=['POST'])
@admin_required
def create_unit():
    """Create a new unit."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO units
                (unit_code, unit_name, credit_hours, programme_id,
                 lecturer_id, semester_number, year_of_study, max_capacity, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("unit_code"),
            data.get("unit_name"),
            data.get("credit_hours", 3),
            data.get("programme_id"),
            data.get("lecturer_id"),
            data.get("semester_number", 1),
            data.get("year_of_study", 1),
            data.get("max_capacity", 100),
            data.get("description")
        ))
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Unit created successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/units/<int:unit_id>', methods=['PUT'])
@admin_required
def update_unit(unit_id):
    """Update a unit."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE units
            SET unit_code = %s,
                unit_name = %s,
                credit_hours = %s,
                programme_id = %s,
                lecturer_id = %s,
                semester_number = %s,
                year_of_study = %s,
                max_capacity = %s,
                description = %s
            WHERE unit_id = %s
        """, (
            data.get("unit_code"),
            data.get("unit_name"),
            data.get("credit_hours"),
            data.get("programme_id"),
            data.get("lecturer_id"),
            data.get("semester_number"),
            data.get("year_of_study"),
            data.get("max_capacity", 100),
            data.get("description"),
            unit_id
        ))
        connection.commit()

        return jsonify({"success": True, "message": "Unit updated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/units/<int:unit_id>', methods=['DELETE'])
@admin_required
def delete_unit(unit_id):
    """Delete a unit."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM units WHERE unit_id = %s", (unit_id,))
        connection.commit()

        return jsonify({"success": True, "message": "Unit deleted."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# MANAGE DEPARTMENTS — CRUD
# =============================================================
@admin_bp.route('/admin/departments', methods=['GET'])
@admin_required
def list_departments():
    """List all departments with school info."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT d.department_id, d.department_name, d.department_code AS department_prefix, d.hod_name AS hod,
                   sch.school_id, sch.school_name
            FROM departments d
            INNER JOIN schools sch ON d.school_id = sch.school_id
            ORDER BY sch.school_name, d.department_name
        """)
        departments = cursor.fetchall()

        return jsonify({"success": True, "departments": departments})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/departments', methods=['POST'])
@admin_required
def create_department():
    """Create a new department."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    dept_name = data.get("department_name", "")
    dept_code = data.get("department_prefix")
    if not dept_code and dept_name:
        dept_code = "".join([w[0] for w in dept_name.split() if w]).upper()[:10]
        if len(dept_code) < 2:
            dept_code = dept_name[:3].upper()

    try:
        cursor.execute("""
            INSERT INTO departments (department_name, department_code, school_id, hod_name)
            VALUES (%s, %s, %s, %s)
        """, (
            dept_name,
            dept_code,
            data.get("school_id"),
            data.get("hod")
        ))
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Department created."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/departments/<int:department_id>', methods=['PUT'])
@admin_required
def update_department(department_id):
    """Update a department."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    dept_name = data.get("department_name", "")
    dept_code = data.get("department_prefix")
    if not dept_code and dept_name:
        dept_code = "".join([w[0] for w in dept_name.split() if w]).upper()[:10]
        if len(dept_code) < 2:
            dept_code = dept_name[:3].upper()

    try:
        cursor.execute("""
            UPDATE departments
            SET department_name = %s, department_code = %s, school_id = %s, hod_name = %s
            WHERE department_id = %s
        """, (
            dept_name,
            dept_code,
            data.get("school_id"),
            data.get("hod"),
            department_id
        ))
        connection.commit()

        return jsonify({"success": True, "message": "Department updated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/departments/<int:department_id>', methods=['DELETE'])
@admin_required
def delete_department(department_id):
    """Delete a department."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM departments WHERE department_id = %s",
            (department_id,)
        )
        connection.commit()

        return jsonify({"success": True, "message": "Department deleted."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# CASCADING DROPDOWNS — Schools → Departments → Courses
# =============================================================
@admin_bp.route('/admin/schools/<int:school_id>/departments', methods=['GET'])
@admin_required
def get_departments_by_school(school_id):
    """Return departments filtered by school_id (for cascading dropdown)."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT department_id, department_name
            FROM departments
            WHERE school_id = %s
            ORDER BY department_name
        """, (school_id,))
        departments = cursor.fetchall()

        return jsonify({"success": True, "departments": departments})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/programmes/<int:programme_id>/units', methods=['GET'])
@admin_required
def get_units_by_programme(programme_id):
    """Return units for a programme (for cascading unit selection)."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT unit_id, unit_code, unit_name
            FROM units
            WHERE programme_id = %s
            ORDER BY year_of_study, semester_number, unit_name
        """, (programme_id,))
        units = cursor.fetchall()

        return jsonify({"success": True, "units": units})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# MANAGE LECTURERS — CRUD
# =============================================================
@admin_bp.route('/admin/lecturers', methods=['GET'])
@admin_required
def list_lecturers():
    """List all lecturers with department info."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT l.lecturer_id, l.lecturer_name, l.email, l.phone,
                   d.department_name, sch.school_name
            FROM lecturers l
            LEFT JOIN departments d ON l.department_id = d.department_id
            LEFT JOIN schools sch ON d.school_id = sch.school_id
            ORDER BY l.lecturer_name
        """)
        lecturers = cursor.fetchall()

        return jsonify({"success": True, "lecturers": lecturers})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/lecturers', methods=['POST'])
@admin_required
def create_lecturer():
    """Create a new lecturer."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO lecturers (lecturer_name, email, phone, department_id)
            VALUES (%s, %s, %s, %s)
        """, (
            data.get("lecturer_name"),
            data.get("email"),
            data.get("phone"),
            data.get("department_id")
        ))
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Lecturer created successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/lecturers/<int:lecturer_id>', methods=['PUT'])
@admin_required
def update_lecturer(lecturer_id):
    """Update a lecturer."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE lecturers
            SET lecturer_name = %s,
                email = %s,
                phone = %s,
                department_id = %s
            WHERE lecturer_id = %s
        """, (
            data.get("lecturer_name"),
            data.get("email"),
            data.get("phone"),
            data.get("department_id"),
            lecturer_id
        ))
        connection.commit()

        return jsonify({"success": True, "message": "Lecturer updated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/lecturers/<int:lecturer_id>', methods=['DELETE'])
@admin_required
def delete_lecturer(lecturer_id):
    """Delete a lecturer."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM lecturers WHERE lecturer_id = %s", (lecturer_id,))
        connection.commit()

        return jsonify({"success": True, "message": "Lecturer deleted."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# MANAGE ANNOUNCEMENTS — CRUD
# =============================================================
@admin_bp.route('/admin/announcements', methods=['GET'])
@admin_required
def list_announcements():
    """List all announcements."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT announcement_id, title, message, target_audience, date_posted
            FROM announcements
            ORDER BY date_posted DESC
        """)
        announcements = cursor.fetchall()

        return jsonify({"success": True, "announcements": announcements})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/announcements', methods=['POST'])
@admin_required
def create_announcement():
    """Create a new announcement."""
    data = request.get_json()

    title = data.get("title", "").strip()
    message = data.get("message", "").strip()
    target_audience = data.get("target_audience", "all")

    if not title or not message:
        return jsonify({
            "success": False,
            "message": "Title and message are required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO announcements (title, message, target_audience, date_posted)
            VALUES (%s, %s, %s, NOW())
        """, (title, message, target_audience))
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Announcement posted successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/announcements/<int:announcement_id>', methods=['DELETE'])
@admin_required
def delete_announcement(announcement_id):
    """Delete an announcement."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM announcements WHERE announcement_id = %s",
            (announcement_id,)
        )
        connection.commit()

        return jsonify({"success": True, "message": "Announcement deleted."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# REPORTS AND EXPORTS
# =============================================================
@admin_bp.route('/admin/export/students/<format>', methods=['GET'])
@admin_required
def export_students(format):
    """Export students data in PDF or Excel format."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                s.student_id,
                s.registration_number,
                s.student_name,
                u.email,
                s.phone,
                s.year_of_study,
                d.department_name,
                sch.school_name,
                u.is_active
            FROM students s
            INNER JOIN users u ON s.user_id = u.user_id
            LEFT JOIN departments d ON s.department_id = d.department_id
            LEFT JOIN schools sch ON d.school_id = sch.school_id
            ORDER BY s.student_name
        """)
        students = cursor.fetchall()

        if format.lower() == 'pdf':
            return export_students_pdf(students)
        elif format.lower() == 'excel':
            return export_students_excel(students)
        else:
            return jsonify({"success": False, "message": "Invalid format. Use 'pdf' or 'excel'."}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/export/registrations/<format>', methods=['GET'])
@admin_required
def export_registrations(format):
    """Export registrations data in PDF or Excel format."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                r.registration_id,
                s.registration_number,
                s.student_name,
                u.unit_code,
                u.unit_name,
                u.credit_hours,
                r.status,
                r.registration_date,
                sem.semester_name,
                sess.academic_year
            FROM registrations r
            INNER JOIN students s ON r.student_id = s.student_id
            INNER JOIN units u ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            INNER JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE sem.is_active = 1
            ORDER BY r.registration_date DESC
        """)
        registrations = cursor.fetchall()

        if format.lower() == 'pdf':
            return export_registrations_pdf(registrations)
        elif format.lower() == 'excel':
            return export_registrations_excel(registrations)
        else:
            return jsonify({"success": False, "message": "Invalid format. Use 'pdf' or 'excel'."}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


def export_students_pdf(students):
    """Generate PDF export for students data."""
    from flask import make_response
    import io
    
    # Simple CSV-style export for now (can be upgraded to proper PDF later)
    output = io.StringIO()
    output.write("Student ID,Registration Number,Name,Email,Phone,Year,Department,School,Status\n")
    
    for student in students:
        status = "Active" if student['is_active'] else "Inactive"
        output.write(f"{student['student_id']},{student['registration_number'] or 'N/A'},"
                    f"{student['student_name']},{student['email']},{student['phone'] or 'N/A'},"
                    f"{student['year_of_study']},{student['department_name'] or 'N/A'},"
                    f"{student['school_name'] or 'N/A'},{status}\n")
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=students_report.csv'
    return response


def export_students_excel(students):
    """Generate Excel export for students data."""
    return export_students_pdf(students)  # Same as CSV for now


def export_registrations_pdf(registrations):
    """Generate PDF export for registrations data."""
    from flask import make_response
    import io
    
    output = io.StringIO()
    output.write("Registration ID,Student Number,Student Name,Course Code,Course Name,Credits,Status,Date,Semester,Year\n")
    
    for reg in registrations:
        output.write(f"{reg['registration_id']},{reg['registration_number'] or 'N/A'},"
                    f"{reg['student_name']},{reg['course_code']},{reg['course_name']},"
                    f"{reg['credit_hours']},{reg['status']},{reg['registration_date']},"
                    f"{reg['semester_name']},{reg['academic_year']}\n")
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=registrations_report.csv'
    return response


def export_registrations_excel(registrations):
    """Generate Excel export for registrations data."""
    return export_registrations_pdf(registrations)  # Same as CSV for now


# =============================================================
# MANAGE SCHOOLS — CRUD
# =============================================================
@admin_bp.route('/admin/schools', methods=['GET'])
@admin_required
def list_schools():
    """List all schools."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT sch.school_id, sch.school_name, sch.dean,
                   COUNT(d.department_id) AS department_count
            FROM schools sch
            LEFT JOIN departments d ON sch.school_id = d.school_id
            GROUP BY sch.school_id, sch.school_name, sch.dean
            ORDER BY sch.school_name
        """)
        schools = cursor.fetchall()

        return jsonify({"success": True, "schools": schools})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/schools', methods=['POST'])
@admin_required
def create_school():
    """Create a new school."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO schools (school_name, dean) VALUES (%s, %s)",
            (data.get("school_name"), data.get("dean"))
        )
        connection.commit()

        return jsonify({
            "success": True,
            "message": "School created."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/schools/<int:school_id>', methods=['PUT'])
@admin_required
def update_school(school_id):
    """Update a school."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE schools SET school_name = %s, dean = %s WHERE school_id = %s",
            (data.get("school_name"), data.get("dean"), school_id)
        )
        connection.commit()

        return jsonify({"success": True, "message": "School updated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/schools/<int:school_id>', methods=['DELETE'])
@admin_required
def delete_school(school_id):
    """Delete a school."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM schools WHERE school_id = %s",
            (school_id,)
        )
        connection.commit()

        return jsonify({"success": True, "message": "School deleted."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# MANAGE SEMESTERS — CRUD
# =============================================================
@admin_bp.route('/admin/semesters', methods=['GET'])
@admin_required
def list_semesters():
    """List all semesters."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM semesters
            ORDER BY academic_year DESC, semester_name DESC
        """)
        semesters = cursor.fetchall()

        return jsonify({"success": True, "semesters": semesters})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/semesters', methods=['POST'])
@admin_required
def create_semester():
    """Create a new semester."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # If this is set as active, deactivate all others first
        if data.get("is_active"):
            cursor.execute("UPDATE semesters SET is_active = 0")

        cursor.execute("""
            INSERT INTO semesters
                (semester_name, academic_year, start_date, end_date,
                 registration_deadline, is_active, is_registration_open)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("semester_name"),
            data.get("academic_year"),
            data.get("start_date"),
            data.get("end_date"),
            data.get("registration_deadline"),
            data.get("is_active", 0),
            data.get("is_registration_open", 1)
        ))
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Semester created."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/semesters/<int:semester_id>', methods=['PUT'])
@admin_required
def update_semester(semester_id):
    """Update a semester."""
    data = request.get_json()

    connection = get_connection()
    cursor = connection.cursor()

    try:
        if data.get("is_active"):
            cursor.execute("UPDATE semesters SET is_active = 0")

        cursor.execute("""
            UPDATE semesters
            SET semester_name = %s,
                academic_year = %s,
                start_date = %s,
                end_date = %s,
                registration_deadline = %s,
                is_active = %s,
                is_registration_open = %s
            WHERE semester_id = %s
        """, (
            data.get("semester_name"),
            data.get("academic_year"),
            data.get("start_date"),
            data.get("end_date"),
            data.get("registration_deadline"),
            data.get("is_active", 0),
            data.get("is_registration_open", 1),
            semester_id
        ))
        connection.commit()

        return jsonify({"success": True, "message": "Semester updated."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# APPROVE / REJECT REGISTRATIONS
# =============================================================
@admin_bp.route('/admin/registrations', methods=['GET'])
@admin_required
def list_registrations():
    """List all registration requests with filters."""
    status_filter = request.args.get('status', '').strip()
    keyword = request.args.get('keyword', '').strip()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                r.registration_id,
                s.student_name,
                s.registration_number,
                u.unit_code AS course_code,
                u.unit_name AS course_name,
                r.status,
                r.registration_date,
                sem.semester_name,
                ac.academic_year
            FROM registrations r
            INNER JOIN students s ON r.student_id = s.student_id
            INNER JOIN units u ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            INNER JOIN academic_sessions ac ON sem.session_id = ac.session_id
        """

        conditions = []
        params = []

        if status_filter:
            conditions.append("r.status = %s")
            params.append(status_filter)

        if keyword:
            conditions.append(
                "(s.student_name LIKE %s OR s.registration_number LIKE %s)"
            )
            search = f"%{keyword}%"
            params.extend([search, search])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.registration_date DESC"

        cursor.execute(query, tuple(params))
        registrations = cursor.fetchall()

        return jsonify({"success": True, "registrations": registrations})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/registrations/<int:registration_id>/approve', methods=['PUT'])
@admin_required
def approve_registration(registration_id):
    """
    Approve a pending registration.

    If the student doesn't have a registration number yet, generate one
    using the format: [DEPT_PREFIX][YEAR][4-DIGIT-SEQUENCE]
    e.g. CS20260001, IT20260002
    """
    admin_id = session.get('admin_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE registrations
            SET status = 'approved',
                approved_by = %s,
                approved_at = NOW()
            WHERE registration_id = %s AND status = 'pending'
        """, (admin_id, registration_id))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Registration not found or already processed."
            }), 404

        # Get student info for notification and check registration number
        cursor.execute("""
            SELECT r.student_id, s.user_id, s.registration_number, u.unit_code, p.programme_code AS programme_prefix
            FROM registrations r
            INNER JOIN students s ON r.student_id = s.student_id
            INNER JOIN units u ON r.unit_id = u.unit_id
            LEFT JOIN programmes p ON s.programme_id = p.programme_id
            WHERE r.registration_id = %s
        """, (registration_id,))
        reg_info = cursor.fetchone()

        if reg_info:
            student_id = reg_info['student_id']
            prog_prefix = reg_info['programme_prefix'] or 'STU'
            year = datetime.now().year
            current_reg = reg_info['registration_number']
            new_reg_number = current_reg

            if not current_reg:
                # Generate new registration number
                pattern = f"{prog_prefix}/{year}/%"
                cursor.execute("""
                    SELECT registration_number FROM students
                    WHERE registration_number LIKE %s
                    ORDER BY registration_number DESC LIMIT 1
                """, (pattern,))
                last_row = cursor.fetchone()
                
                if last_row and last_row['registration_number']:
                    last_num = last_row['registration_number']
                    prefix_len = len(prog_prefix) + 6 # prefix + /YYYY/
                    seq_str = last_num[prefix_len:]
                    try:
                        next_seq = int(seq_str) + 1
                    except ValueError:
                        next_seq = 1
                else:
                    next_seq = 1
                    
                new_reg_number = f"{prog_prefix}/{year}/{next_seq:04d}"
                
                # Update student record
                cursor.execute("""
                    UPDATE students 
                    SET registration_number = %s
                    WHERE student_id = %s
                """, (new_reg_number, student_id))
            
            # Create notification for student
            msg = f"Your registration for course {reg_info['unit_code']} has been approved."
            if not current_reg:
                msg += f" Your official registration number is now {new_reg_number}."
                
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message)
                VALUES (%s, %s, %s)
            """, (
                reg_info['user_id'],
                'Course Registration Approved',
                msg
            ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Course registration approved."
        })

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# APPROVE / REJECT ADMISSION APPLICATIONS
# =============================================================
@admin_bp.route('/admin/applications', methods=['GET'])
@admin_required
def list_applications():
    """List all admission applications with KCSE and programme info."""
    status_filter = request.args.get('status', '').strip()
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                a.application_id, a.status, a.applied_at,
                s.student_id, s.student_name, u.email, s.phone,
                p.programme_name, p.programme_code AS programme_prefix, p.requirements,
                k.kcse_year, k.index_number, k.mean_grade
            FROM applications a
            INNER JOIN students s ON a.student_id = s.student_id
            INNER JOIN users u ON s.user_id = u.user_id
            INNER JOIN programmes p ON a.programme_id = p.programme_id
            LEFT JOIN kcse_info k ON s.student_id = k.student_id
        """
        params = []
        if status_filter:
            query += " WHERE a.status = %s"
            params.append(status_filter)
            
        query += " ORDER BY a.applied_at DESC"

        cursor.execute(query, tuple(params))
        applications = cursor.fetchall()
        
        # Fetch grades for each
        for app in applications:
            cursor.execute("SELECT subject, grade FROM kcse_grades WHERE student_id = %s", (app['student_id'],))
            app['kcse_grades'] = cursor.fetchall()

        return jsonify({"success": True, "applications": applications})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/applications/<int:application_id>/approve', methods=['PUT'])
@admin_required
def approve_application(application_id):
    """
    Approve an admission application.
    Generates a registration number: [PROG_PREFIX][YEAR][SEQ] (e.g. CS20260001)
    """
    admin_id = session.get('admin_id')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check application
        cursor.execute("""
            SELECT a.student_id, a.programme_id, s.user_id, s.registration_number,
                   p.programme_code AS programme_prefix, p.department_id, p.programme_name
            FROM applications a
            INNER JOIN students s ON a.student_id = s.student_id
            INNER JOIN programmes p ON a.programme_id = p.programme_id
            WHERE a.application_id = %s AND a.status = 'pending'
        """, (application_id,))
        app_info = cursor.fetchone()

        if not app_info:
            return jsonify({"success": False, "message": "Application not found or already processed."}), 404

        # Update application status
        cursor.execute("""
            UPDATE applications
            SET status = 'approved', approved_by = %s, reviewed_at = NOW()
            WHERE application_id = %s
        """, (admin_id, application_id))

        student_id = app_info['student_id']
        prog_id = app_info['programme_id']
        dept_id = app_info['department_id']
        prog_prefix = app_info['programme_prefix'] or 'STU'
        year = datetime.now().year
        new_reg_number = app_info['registration_number']

        # Generate registration number if none exists
        if not new_reg_number:
            pattern = f"{prog_prefix}/{year}/%"
            cursor.execute("""
                SELECT registration_number FROM students
                WHERE registration_number LIKE %s
                ORDER BY registration_number DESC LIMIT 1
            """, (pattern,))
            last_row = cursor.fetchone()

            if last_row and last_row['registration_number']:
                last_num = last_row['registration_number']
                prefix_len = len(prog_prefix) + 6 # prefix + '/YYYY/'
                seq_str = last_num[prefix_len:]
                try:
                    next_seq = int(seq_str) + 1
                except ValueError:
                    next_seq = 1
            else:
                next_seq = 1

            new_reg_number = f"{prog_prefix}/{year}/{next_seq:04d}"

        # Update student record (lock programme, assign dept and reg number)
        cursor.execute("""
            UPDATE students 
            SET programme_id = %s, department_id = %s, registration_number = %s
            WHERE student_id = %s
        """, (prog_id, dept_id, new_reg_number, student_id))

        # Auto-assign programme units to student
        # Get active semester
        cursor.execute("""
            SELECT semester_id FROM semesters WHERE is_active = 1 LIMIT 1
        """)
        sem_row = cursor.fetchone()
        
        if sem_row:
            semester_id = sem_row['semester_id']
            
            # Get all units for this programme (matching year of study 1, semester 1 for new students)
            cursor.execute("""
                SELECT unit_id FROM units 
                WHERE programme_id = %s AND year_of_study = 1 AND semester_number = 1
            """, (prog_id,))
            units = cursor.fetchall()
            
            # Auto-register the student for these units
            for unit in units:
                cursor.execute("""
                    INSERT IGNORE INTO registrations 
                    (student_id, unit_id, semester_id, status, registration_date)
                    VALUES (%s, %s, %s, 'approved', NOW())
                """, (student_id, unit['unit_id'], semester_id))

        # Notify student
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message)
            VALUES (%s, %s, %s)
        """, (
            app_info['user_id'],
            'Admission Approved',
            f"Congratulations! Your admission to {app_info['programme_name']} has been approved. Your registration number is {new_reg_number}."
        ))

        connection.commit()
        return jsonify({
            "success": True, 
            "message": f"Admission approved. Registration number {new_reg_number} assigned and units auto-enrolled."
        })

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/applications/<int:application_id>/reject', methods=['PUT'])
@admin_required
def reject_application(application_id):
    """Reject an admission application."""
    data = request.get_json()
    reason = data.get("reason", "Did not meet minimum requirements.") if data else "Did not meet minimum requirements."
    admin_id = session.get('admin_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT a.student_id, s.user_id, p.programme_name
            FROM applications a
            INNER JOIN students s ON a.student_id = s.student_id
            INNER JOIN programmes p ON a.programme_id = p.programme_id
            WHERE a.application_id = %s AND a.status = 'pending'
        """, (application_id,))
        app_info = cursor.fetchone()

        if not app_info:
            return jsonify({"success": False, "message": "Application not found or already processed."}), 404

        cursor.execute("""
            UPDATE applications
            SET status = 'rejected', approved_by = %s, reviewed_at = NOW()
            WHERE application_id = %s
        """, (admin_id, application_id))

        # Notify student
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message)
            VALUES (%s, %s, %s)
        """, (
            app_info['user_id'],
            'Admission Rejected',
            f"Your application for {app_info['programme_name']} was rejected. Reason: {reason}"
        ))

        connection.commit()
        return jsonify({"success": True, "message": "Application rejected."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@admin_bp.route('/admin/registrations/<int:registration_id>/reject', methods=['PUT'])
@admin_required
def reject_registration(registration_id):
    """Reject a pending registration."""
    data = request.get_json()
    reason = data.get("reason", "No reason provided.") if data else "No reason provided."
    admin_id = session.get('admin_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE registrations
            SET status = 'rejected',
                approved_by = %s,
                approved_at = NOW()
            WHERE registration_id = %s AND status = 'pending'
        """, (admin_id, registration_id))

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Registration not found or already processed."
            }), 404

        # Get student info for notification
        cursor.execute("""
            SELECT r.student_id, s.user_id, u.unit_code
            FROM registrations r
            INNER JOIN students s ON r.student_id = s.student_id
            INNER JOIN units u ON r.unit_id = u.unit_id
            WHERE r.registration_id = %s
        """, (registration_id,))
        reg_info = cursor.fetchone()

        if reg_info:
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message)
                VALUES (%s, %s, %s)
            """, (
                reg_info['user_id'],
                'Registration Rejected',
                f"Your registration for {reg_info['unit_code']} was rejected. Reason: {reason}"
            ))

        connection.commit()

        return jsonify({"success": True, "message": "Registration rejected."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()
