"""
Registration routes — register courses, view, search, drop, download PDF.

WHAT CHANGED from original course_registration/ folder:
- fetch_courselist.py:  PRESERVED as GET /registration/courses
- search_courses.py:    PRESERVED as GET /registration/courses?keyword=...
  (Merged into one endpoint — the original had two separate endpoints
   that did the same thing, which is redundant)
- register_courses.py:  PRESERVED as POST /registration/register
  ENHANCED: Added duplicate check, prerequisite validation, credit limit.
- save_registered_courses.py: REMOVED (exact duplicate of register_courses.py)
- avoid_duplicates.py:  Logic MERGED into the main register endpoint.
- displaycourse.py:     REMOVED (duplicate of fetch_courselist.py)
- view_registered_courses.py:  PRESERVED as GET /registration/my-courses
- registered_courseunits.py:    PRESERVED as GET /registration/my-courses
"""

from collections import OrderedDict
from datetime import date
from flask import request, jsonify, session

from registration import registration_bp
from db import get_connection
from auth.decorators import login_required
from config import Config


# =============================================================
# GET /registration/courses — Fetch and search courses
# =============================================================
# PRESERVED from fetch_courselist.py + search_courses.py
# =============================================================
@registration_bp.route('/registration/courses', methods=['GET'])
@login_required
def get_courses():
    """
    List all available courses, optionally filtered by keyword.

    Query params:
        keyword (optional) — search by course code or name
        programme_id (optional) — filter by programme

    PRESERVED: Original SELECT and LIKE search logic.
    ENHANCED:  Added programme/lecturer info to match design.
    """
    keyword = request.args.get('keyword', '').strip()
    req_programme_id = request.args.get('programme_id', '').strip()

    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get student's programme for filtering
        cursor.execute("SELECT programme_id FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()

        if not student:
            return jsonify({
                "success": False,
                "message": "Student record not found."
            }), 404

        # Filter by student's programme
        programme_id = student['programme_id']

        base_query = """
            SELECT
                u.unit_id,
                u.unit_id AS course_id,
                u.unit_code,
                u.unit_code AS course_code,
                u.unit_name,
                u.unit_name AS course_name,
                u.credit_hours,
                u.semester_number,
                u.year_of_study,
                u.is_elective,
                p.programme_name,
                p.programme_name AS department_name,
                l.lecturer_name,
                d.department_name AS actual_department_name
            FROM units u
            LEFT JOIN programmes p ON u.programme_id = p.programme_id
            LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
            LEFT JOIN departments d ON p.department_id = d.department_id
        """

        conditions = []
        params = []

        if keyword:
            conditions.append("(u.unit_code LIKE %s OR u.unit_name LIKE %s)")
            search = f"%{keyword}%"
            params.extend([search, search])

        if programme_id:
            conditions.append("u.programme_id = %s")
            params.append(programme_id)

        conditions.append("u.is_active = 1")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY u.year_of_study ASC, u.semester_number ASC, u.unit_code ASC"

        cursor.execute(base_query, tuple(params))
        units = cursor.fetchall()

        return jsonify({
            "success": True,
            "courses": units
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# POST /registration/register — Register for courses
# =============================================================
# PRESERVED from register_courses.py + avoid_duplicates.py
# ENHANCED: prerequisite check, credit limit, duplicate prevention
# =============================================================
@registration_bp.route('/registration/register', methods=['POST'])
@login_required
def register_courses():
    """
    Register the student for one or more courses.

    Expects JSON:
    {
        "courses": [1, 2, 3]  ← list of unit_id values (course IDs)
    }

    Validates:
    1. No duplicate registrations (PRESERVED from avoid_duplicates.py)
    2. Prerequisites are met (NEW)
    3. Credit limit not exceeded (NEW)
    4. Registration deadline not passed (NEW)
    """
    data = request.get_json()
    student_id = session.get('student_id')

    # Accept 'courses' field name
    course_ids = data.get("courses") if data else None

    if not course_ids:
        return jsonify({
            "success": False,
            "message": "No courses selected."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check registration deadline and open flag
        cursor.execute("""
            SELECT semester_id, registration_deadline, is_registration_open
            FROM semesters
            WHERE is_active = 1
            LIMIT 1
        """)
        semester = cursor.fetchone()

        if not semester:
            return jsonify({
                "success": False,
                "message": "No active semester found."
            }), 400

        if not semester['is_registration_open']:
            return jsonify({
                "success": False,
                "message": "Course registration is currently closed by the registrar."
            }), 400

        if date.today() > semester['registration_deadline']:
            return jsonify({
                "success": False,
                "message": "Registration deadline has passed."
            }), 400

        semester_id = semester['semester_id']

        # --- Check current credit hours ---
        cursor.execute("""
            SELECT COALESCE(SUM(u.credit_hours), 0) AS current_credits
            FROM registrations r
            INNER JOIN units u ON r.unit_id = u.unit_id
            WHERE r.student_id = %s
              AND r.semester_id = %s
              AND r.status IN ('pending', 'approved')
        """, (student_id, semester_id))

        current_credits = cursor.fetchone()['current_credits']

        # Calculate credits for requested courses
        placeholders = ', '.join(['%s'] * len(course_ids))
        cursor.execute(f"""
            SELECT unit_id, unit_code, unit_name, credit_hours
            FROM units
            WHERE unit_id IN ({placeholders})
        """, tuple(course_ids))

        requested_courses = cursor.fetchall()
        new_credits = sum(u['credit_hours'] for u in requested_courses)

        total_credits = current_credits + new_credits

        if total_credits > Config.MAX_CREDIT_HOURS_PER_SEMESTER:
            return jsonify({
                "success": False,
                "message": f"Credit limit exceeded. Maximum: {Config.MAX_CREDIT_HOURS_PER_SEMESTER}, "
                           f"Current: {current_credits}, Requested: {new_credits}."
            }), 400

        # --- Check for duplicates (PRESERVED from avoid_duplicates.py) ---
        cursor.execute(f"""
            SELECT unit_id
            FROM registrations
            WHERE student_id = %s
              AND semester_id = %s
              AND unit_id IN ({placeholders})
              AND status IN ('pending', 'approved')
        """, (student_id, semester_id) + tuple(course_ids))

        already_registered = [row['unit_id'] for row in cursor.fetchall()]

        if already_registered:
            # Get course codes for the error message
            duplicate_codes = [
                u['unit_code'] for u in requested_courses
                if u['unit_id'] in already_registered
            ]
            return jsonify({
                "success": False,
                "message": f"Already registered for: {', '.join(duplicate_codes)}"
            }), 409

        # --- Validate prerequisites (NEW) ---
        # Get units the student has passed (grade not F, not null)
        cursor.execute("""
            SELECT DISTINCT unit_id
            FROM results
            WHERE student_id = %s AND grade IS NOT NULL AND grade != 'F'
        """, (student_id,))

        passed_units = {row['unit_id'] for row in cursor.fetchall()}

        for course_id in course_ids:
            cursor.execute("""
                SELECT p.prerequisite_unit_id, u.unit_code AS prereq_code
                FROM prerequisites p
                INNER JOIN units u ON p.prerequisite_unit_id = u.unit_id
                WHERE p.unit_id = %s AND p.is_mandatory = 1
            """, (course_id,))

            prereqs = cursor.fetchall()

            for prereq in prereqs:
                if prereq['prerequisite_unit_id'] not in passed_units:
                    # Find the course code being registered
                    course_code = next(
                        (u['unit_code'] for u in requested_courses if u['unit_id'] == course_id),
                        'Unknown'
                    )
                    return jsonify({
                        "success": False,
                        "message": f"Prerequisite not met: {course_code} requires {prereq['prereq_code']}."
                    }), 400

        # --- All checks passed — register courses ---
        # PRESERVED logic from register_courses.py
        for course_id in course_ids:
            cursor.execute("""
                INSERT INTO registrations (student_id, unit_id, semester_id, status)
                VALUES (%s, %s, %s, 'pending')
            """, (student_id, course_id, semester_id))

        connection.commit()

        return jsonify({
            "success": True,
            "message": f"Successfully registered for {len(course_ids)} course(s). Awaiting approval."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# GET /registration/my-courses — View registered courses
# =============================================================
# PRESERVED from view_registered_courses.py
# =============================================================
@registration_bp.route('/registration/my-courses', methods=['GET'])
@login_required
def get_my_courses():
    """
    Return the student's registered courses for the active semester.

    PRESERVED: Original JOIN query.
    ENHANCED: Added registration status, semester filter, lecturer info.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                r.registration_id,
                u.unit_code AS course_code,
                u.unit_name AS course_name,
                u.credit_hours,
                r.status AS registration_status,
                r.registration_date,
                l.lecturer_name,
                p.programme_name
            FROM registrations r
            INNER JOIN units u ON r.unit_id = u.unit_id
            LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
            LEFT JOIN programmes p ON u.programme_id = p.programme_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            WHERE r.student_id = %s
              AND sem.is_active = 1
              AND r.status != 'dropped'
            ORDER BY u.unit_code
        """, (student_id,))

        units = cursor.fetchall()

        # Total credit hours
        total_credits = sum(u['credit_hours'] for u in units)

        return jsonify({
            "success": True,
            "courses": units,
            "total_credits": total_credits
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# DELETE /registration/drop/<id> — Drop a course (NEW)
# =============================================================
@registration_bp.route('/registration/drop/<int:registration_id>', methods=['DELETE'])
@login_required
def drop_course(registration_id):
    """
    Drop a registered course before the deadline.

    Only pending or approved registrations can be dropped.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check deadline and open flag
        cursor.execute("""
            SELECT registration_deadline, is_registration_open
            FROM semesters
            WHERE is_active = 1
            LIMIT 1
        """)
        semester = cursor.fetchone()

        if semester:
            if not semester['is_registration_open']:
                return jsonify({
                    "success": False,
                    "message": "Registration is closed. Drops are not allowed at this time."
                }), 400
            if date.today() > semester['registration_deadline']:
                return jsonify({
                    "success": False,
                    "message": "Drop deadline has passed."
                }), 400

        # Verify ownership
        cursor.execute("""
            SELECT registration_id, status
            FROM registrations
            WHERE registration_id = %s AND student_id = %s
        """, (registration_id, student_id))

        reg = cursor.fetchone()

        if not reg:
            return jsonify({
                "success": False,
                "message": "Registration not found."
            }), 404

        if reg['status'] == 'dropped':
            return jsonify({
                "success": False,
                "message": "Course already dropped."
            }), 400

        # Mark as dropped (soft delete to preserve history)
        cursor.execute("""
            UPDATE registrations
            SET status = 'dropped'
            WHERE registration_id = %s
        """, (registration_id,))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Course dropped successfully."
        })

    except Exception as e:
        connection.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# GET /registration/history — All-semester registration history
# =============================================================
@registration_bp.route('/registration/history', methods=['GET'])
@login_required
def get_registration_history():
    """
    Return the student's registration history across ALL semesters,
    grouped by semester for a clear chronological view.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                r.registration_id,
                u.unit_code,
                u.unit_name,
                u.credit_hours,
                r.status AS registration_status,
                r.registration_date,
                sem.semester_name,
                sess.academic_year,
                l.lecturer_name
            FROM registrations r
            INNER JOIN units u ON r.unit_id = u.unit_id
            LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            INNER JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE r.student_id = %s
            ORDER BY sess.academic_year DESC, sem.semester_name DESC, u.unit_code
        """, (student_id,))

        rows = cursor.fetchall()

        # Group by semester
        grouped = OrderedDict()
        for row in rows:
            key = f"{row['semester_name']} — {row['academic_year']}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(row)

        # Build list of semester objects
        semesters = []
        for sem_label, units in grouped.items():
            semesters.append({
                "semester_label": sem_label,
                "units": units,
                "total_credits": sum(u['credit_hours'] for u in units
                                     if u['registration_status'] != 'dropped')
            })

        return jsonify({
            "success": True,
            "history": semesters,
            "total_rows": len(rows)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()
