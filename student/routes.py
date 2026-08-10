"""
Student routes — dashboard, profile (view/edit/photo/password), results, timetable.

WHAT CHANGED from original files:
- dashboard.py: Logic PRESERVED. Added notification count, semester info.
  Route preserved as GET /student/dashboard.
- profile.py: Was read-only. Now supports GET, PUT (edit), POST (photo),
  and PUT /student/change-password.
- results.py: Was basic marks query. Now calculates semester GPA,
  cumulative GPA, and generates remarks.
- timetable.py: Logic PRESERVED. Added conflict detection endpoint.
"""

import os
from flask import request, jsonify, session

from student import student_bp
from db import get_connection
from auth.decorators import login_required
from extensions import bcrypt
from config import Config


# =============================================================
# GET /student/dashboard
# =============================================================
# Original code from dashboard.py — PRESERVED and enhanced
# =============================================================
@student_bp.route('/student/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Return dashboard data for the logged-in student.

    Returns: student info, registered course count, GPA,
    announcements, notification count, active semester.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Student Information — includes programme for dashboard header
        cursor.execute("""
            SELECT
                s.student_name,
                s.registration_number,
                s.phone,
                s.year_of_study,
                d.department_name,
                sch.school_name AS school_name,
                p.programme_name,
                p.programme_code
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.department_id
            LEFT JOIN schools sch ON d.school_id = sch.school_id
            LEFT JOIN programmes p ON s.programme_id = p.programme_id
            WHERE s.student_id = %s
        """, (student_id,))
        student = cursor.fetchone()

        # Check if student has an approved application
        cursor.execute("""
            SELECT COUNT(*) AS approved_count
            FROM applications
            WHERE student_id = %s AND status = 'approved'
        """, (student_id,))
        app_row = cursor.fetchone()
        is_approved = (app_row['approved_count'] > 0) if app_row else False

        # Total Registered Units (PRESERVED from original)
        cursor.execute("""
            SELECT COUNT(*) AS total_units
            FROM registrations
            WHERE student_id = %s
              AND status IN ('pending', 'approved')
        """, (student_id,))
        total_units = cursor.fetchone()

        # Current GPA (PRESERVED from original, enhanced)
        cursor.execute("""
            SELECT
                ROUND(
                    SUM(r.grade_points * u.credit_hours) /
                    NULLIF(SUM(u.credit_hours), 0),
                2) AS gpa
            FROM results r
            INNER JOIN units u ON r.unit_id = u.unit_id
            WHERE r.student_id = %s
        """, (student_id,))
        gpa_row = cursor.fetchone()
        gpa = gpa_row['gpa'] if gpa_row and gpa_row['gpa'] else 0.00

        # Recent Announcements (PRESERVED from original)
        cursor.execute("""
            SELECT
                title,
                message,
                date_posted
            FROM announcements
            WHERE target_audience IN ('all', 'students')
            ORDER BY date_posted DESC
            LIMIT 5
        """)
        announcements = cursor.fetchall()

        # NEW — Unread notification count
        user_id = session.get('user_id')
        cursor.execute("""
            SELECT COUNT(*) AS unread_count
            FROM notifications
            WHERE user_id = %s AND is_read = 0
        """, (user_id,))
        notif_row = cursor.fetchone()
        unread_notifications = notif_row['unread_count'] if notif_row else 0

        # NEW — Active semester
        cursor.execute("""
            SELECT sem.semester_name, sess.academic_year
            FROM semesters sem
            LEFT JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE sem.is_active = 1
            LIMIT 1
        """)
        semester = cursor.fetchone()

        return jsonify({
            "success": True,
            "student": student,
            "registered_units": total_units["total_units"] if total_units else 0,
            "gpa": float(gpa),
            "announcements": announcements,
            "unread_notifications": unread_notifications,
            "semester": semester,
            "is_approved": is_approved,
            "programme_name": student.get('programme_name') if student else None
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
# GET /student/profile
# =============================================================
# Original code from profile.py — PRESERVED and enhanced
# =============================================================
@student_bp.route('/student/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Return the current student's full profile.

    PRESERVED: Original SELECT * logic.
    ENHANCED: Added department and school joins, proper error handling.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                s.student_id,
                s.registration_number,
                s.student_name,
                s.phone,
                s.year_of_study,
                s.profile_photo,
                u.email,
                d.department_name,
                sch.school_name AS school_name
            FROM students s
            INNER JOIN users u ON s.user_id = u.user_id
            LEFT JOIN departments d ON s.department_id = d.department_id
            LEFT JOIN schools sch ON d.school_id = sch.school_id
            WHERE s.student_id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        return jsonify({
            "success": True,
            "student": student
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
# PUT /student/profile — Edit profile (NEW)
# =============================================================
@student_bp.route('/student/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Update the student's profile fields.

    Expects JSON: { "student_name": "...", "phone": "..." }
    """
    data = request.get_json()
    student_id = session.get('student_id')

    name = data.get("student_name", "").strip() if data else ""
    phone = data.get("phone", "").strip() if data else ""

    if not name:
        return jsonify({
            "success": False,
            "message": "Name is required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE students
            SET student_name = %s,
                phone = %s
            WHERE student_id = %s
        """, (name, phone, student_id))

        connection.commit()

        # Update session name
        session['student_name'] = name

        return jsonify({
            "success": True,
            "message": "Profile updated successfully."
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
# POST /student/profile/photo — Upload profile photo (NEW)
# =============================================================
@student_bp.route('/student/profile/photo', methods=['POST'])
@login_required
def upload_profile_photo():
    """
    Upload a profile photo for the current student.

    Expects: multipart/form-data with a 'photo' file field.
    """
    if 'photo' not in request.files:
        return jsonify({
            "success": False,
            "message": "No photo file provided."
        }), 400

    photo = request.files['photo']

    if photo.filename == '':
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    # Validate extension
    extension = photo.filename.rsplit('.', 1)[-1].lower() if '.' in photo.filename else ''
    if extension not in Config.ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "message": f"Allowed file types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        }), 400

    student_id = session.get('student_id')

    # Create uploads directory if it doesn't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Save file with unique name
    filename = f"student_{student_id}.{extension}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    photo.save(filepath)

    # Update database
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE students SET profile_photo = %s WHERE student_id = %s",
            (filename, student_id)
        )
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Profile photo uploaded.",
            "filename": filename
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
# PUT /student/change-password (NEW)
# =============================================================
@student_bp.route('/student/change-password', methods=['PUT'])
@login_required
def change_password():
    """
    Change the current user's password.

    Expects JSON: { "current_password": "...", "new_password": "..." }
    """
    data = request.get_json()

    current_password = data.get("current_password", "").strip() if data else ""
    new_password = data.get("new_password", "").strip() if data else ""

    if not current_password or not new_password:
        return jsonify({
            "success": False,
            "message": "Both current and new passwords are required."
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "success": False,
            "message": "New password must be at least 6 characters."
        }), 400

    user_id = session.get('user_id')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Verify current password
        cursor.execute(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not bcrypt.check_password_hash(user['password_hash'], current_password):
            return jsonify({
                "success": False,
                "message": "Current password is incorrect."
            }), 401

        # Hash and update new password
        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_hash, user_id)
        )
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Password changed successfully."
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
# GET /student/results
# =============================================================
# Original code from results.py — PRESERVED and enhanced
# =============================================================
@student_bp.route('/student/results', methods=['GET'])
@login_required
def results():
    """
    Return results with GPA calculation.

    PRESERVED: Original query for marks and grades.
    ENHANCED: Added semester GPA, cumulative GPA, and remarks.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Unit results — aliased as course_code/course_name for frontend compatibility
        cursor.execute("""
            SELECT
                u.unit_code  AS course_code,
                u.unit_name  AS course_name,
                u.unit_code,
                u.unit_name,
                u.credit_hours,
                r.cat_marks,
                r.exam_marks,
                r.total_marks,
                r.grade,
                r.grade_points,
                r.remarks,
                sem.semester_name,
                sess.academic_year
            FROM results r
            INNER JOIN units u ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            INNER JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE r.student_id = %s AND r.is_published = 1
            ORDER BY sess.academic_year DESC, sem.semester_name DESC, u.unit_code
        """, (student_id,))

        course_results = cursor.fetchall()

        # Calculate average marks
        total_sum = sum(float(r['total_marks']) for r in course_results if r['total_marks'])
        average_marks = round(total_sum / len(course_results), 1) if course_results else 0

        # Add remarks if not set by DB
        for row in course_results:
            if not row.get('remarks'):
                total = float(row['total_marks']) if row['total_marks'] else 0
                if total >= 70:
                    row['remarks'] = 'Distinction'
                elif total >= 60:
                    row['remarks'] = 'Credit'
                elif total >= 50:
                    row['remarks'] = 'Pass'
                elif total >= 40:
                    row['remarks'] = 'Supplementary'
                else:
                    row['remarks'] = 'Fail'

        # Semester GPA (latest semester)
        cursor.execute("""
            SELECT
                sem.semester_name,
                sess.academic_year,
                ROUND(
                    SUM(r.grade_points * u.credit_hours) /
                    NULLIF(SUM(u.credit_hours), 0),
                2) AS semester_gpa
            FROM results r
            INNER JOIN units u ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            INNER JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE r.student_id = %s
            GROUP BY r.semester_id, sem.semester_name, sess.academic_year
            ORDER BY sess.academic_year DESC, sem.semester_name DESC
        """, (student_id,))

        semester_gpas = cursor.fetchall()

        # Cumulative GPA (all semesters)
        cursor.execute("""
            SELECT
                ROUND(
                    SUM(r.grade_points * u.credit_hours) /
                    NULLIF(SUM(u.credit_hours), 0),
                2) AS cumulative_gpa
            FROM results r
            INNER JOIN units u ON r.unit_id = u.unit_id
            WHERE r.student_id = %s
        """, (student_id,))

        cum_row = cursor.fetchone()
        cumulative_gpa = float(cum_row['cumulative_gpa']) if cum_row and cum_row['cumulative_gpa'] else 0.00

        # Overall class/remarks
        if cumulative_gpa >= 3.7:
            overall_remarks = 'First Class Honours'
        elif cumulative_gpa >= 3.0:
            overall_remarks = 'Second Class Upper Division'
        elif cumulative_gpa >= 2.5:
            overall_remarks = 'Second Class Lower Division'
        elif cumulative_gpa >= 2.0:
            overall_remarks = 'Pass'
        else:
            overall_remarks = 'Fail'

        return jsonify({
            "success": True,
            "results": course_results,
            "semester_gpas": semester_gpas,
            "cumulative_gpa": cumulative_gpa,
            "overall_remarks": overall_remarks,
            "average_marks": average_marks,
            "total_units": len(course_results)
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
# GET /student/timetable
# =============================================================
# Original code from timetable.py — PRESERVED and enhanced
# =============================================================
@student_bp.route('/student/timetable', methods=['GET'])
@login_required
def timetable():
    """
    Return the student's weekly timetable.

    PRESERVED: Original query with day/time/venue/lecturer.
    ENHANCED: Only shows approved courses in the active semester.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # PRESERVED query from original timetable.py, enhanced with semester filter
        cursor.execute("""
            SELECT
                u.unit_code  AS course_code,
                u.unit_name  AS course_name,
                u.unit_code,
                u.unit_name,
                t.day_of_week AS day,
                t.day_of_week,
                t.start_time,
                t.end_time,
                t.venue,
                t.session_type,
                l.lecturer_name
            FROM timetables t
            INNER JOIN units u ON t.unit_id = u.unit_id
            LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
            INNER JOIN registrations r ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON t.semester_id = sem.semester_id
            WHERE r.student_id = %s
              AND r.status = 'approved'
              AND sem.is_active = 1
            ORDER BY
                FIELD(t.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'),
                t.start_time
        """, (student_id,))

        timetable_data = cursor.fetchall()

        # Convert time objects to strings for JSON serialization
        for row in timetable_data:
            if row.get('start_time'):
                row['start_time'] = str(row['start_time'])
            if row.get('end_time'):
                row['end_time'] = str(row['end_time'])

        return jsonify({
            "success": True,
            "timetable": timetable_data
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
# GET /student/timetable/conflicts — Conflict detection (NEW)
# =============================================================
@student_bp.route('/student/timetable/conflicts', methods=['GET'])
@login_required
def check_timetable_conflicts():
    """
    Check for time conflicts in the student's registered courses.

    A conflict occurs when two courses overlap on the same day and time.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get all timetable entries for student's approved units
        cursor.execute("""
            SELECT
                t.timetable_id,
                u.unit_code,
                u.unit_name,
                t.day_of_week,
                t.start_time,
                t.end_time,
                t.venue
            FROM timetables t
            INNER JOIN units u ON t.unit_id = u.unit_id
            INNER JOIN registrations r ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON t.semester_id = sem.semester_id
            WHERE r.student_id = %s
              AND r.status = 'approved'
              AND sem.is_active = 1
            ORDER BY t.day_of_week, t.start_time
        """, (student_id,))

        entries = cursor.fetchall()

        # Convert times for comparison
        for entry in entries:
            if entry.get('start_time'):
                entry['start_time'] = str(entry['start_time'])
            if entry.get('end_time'):
                entry['end_time'] = str(entry['end_time'])

        # Detect overlaps
        conflicts = []
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                a = entries[i]
                b = entries[j]

                if a['day_of_week'] == b['day_of_week']:
                    # Check time overlap
                    if a['start_time'] < b['end_time'] and b['start_time'] < a['end_time']:
                        conflicts.append({
                            "unit_1": a['unit_code'],
                            "unit_2": b['unit_code'],
                            "day": a['day_of_week'],
                            "time_1": f"{a['start_time']} - {a['end_time']}",
                            "time_2": f"{b['start_time']} - {b['end_time']}"
                        })

        return jsonify({
            "success": True,
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts
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
# GET /student/notifications (NEW)
# =============================================================
@student_bp.route('/student/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Return all notifications for the current user."""
    user_id = session.get('user_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT notification_id, title, message, is_read, created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))

        notifications = cursor.fetchall()

        return jsonify({
            "success": True,
            "notifications": notifications
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
# PUT /student/notifications/<id>/read (NEW)
# =============================================================
@student_bp.route('/student/notifications/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    user_id = session.get('user_id')

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE notification_id = %s AND user_id = %s
        """, (notification_id, user_id))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Notification marked as read."
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
# PUT /student/notifications/read-all — Bulk mark all read (NEW)
# =============================================================
@student_bp.route('/student/notifications/read-all', methods=['PUT'])
@login_required
def mark_all_notifications_read():
    """Mark every unread notification as read for this user."""
    user_id = session.get('user_id')

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0",
            (user_id,)
        )
        connection.commit()

        return jsonify({
            "success": True,
            "message": "All notifications marked as read."
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
# GET /student/my-units — Programme units (NOT registrations)
# =============================================================
@student_bp.route('/student/my-units', methods=['GET'])
@login_required
def my_units():
    """
    Return ALL units belonging to the student's programme and year.
    This is NOT registration-based — units are part of the course/programme.
    Used by the My Units page to show what the student is studying.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get student's programme and year
        cursor.execute("""
            SELECT s.programme_id, s.year_of_study,
                   p.programme_name, p.programme_code
            FROM students s
            LEFT JOIN programmes p ON s.programme_id = p.programme_id
            WHERE s.student_id = %s
        """, (student_id,))
        student = cursor.fetchone()

        if not student or not student['programme_id']:
            return jsonify({
                "success": True,
                "units": [],
                "programme_name": None,
                "message": "No programme assigned yet."
            })

        programme_id = student['programme_id']
        year_of_study = student.get('year_of_study') or 1

        # Get active semester number
        cursor.execute("""
            SELECT semester_number FROM semesters WHERE is_active = 1 LIMIT 1
        """)
        sem_row = cursor.fetchone()
        semester_number = sem_row['semester_number'] if sem_row else 1

        # Get all units for this programme, year, and active semester
        cursor.execute("""
            SELECT
                u.unit_id,
                u.unit_code,
                u.unit_name,
                u.credit_hours,
                u.semester_number,
                u.year_of_study,
                u.description,
                l.lecturer_name
            FROM units u
            LEFT JOIN lecturers l ON u.lecturer_id = l.lecturer_id
            WHERE u.programme_id = %s
              AND u.year_of_study = %s
              AND u.semester_number = %s
              AND u.is_active = 1
            ORDER BY u.unit_code
        """, (programme_id, year_of_study, semester_number))

        units = cursor.fetchall()
        total_credits = sum(u['credit_hours'] for u in units)

        return jsonify({
            "success": True,
            "programme_name": student['programme_name'],
            "programme_code": student['programme_code'],
            "year_of_study": year_of_study,
            "semester_number": semester_number,
            "units": units,
            "total_units": len(units),
            "total_credits": total_credits
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# GET /student/academic-history — Academic progression by year
# =============================================================
@student_bp.route('/student/academic-history', methods=['GET'])
@login_required
def academic_history():
    """
    Return the student's academic history grouped by year and semester.
    Includes: units studied, marks, grades, year averages, overall average.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get student's programme for context
        cursor.execute("""
            SELECT s.programme_id, s.year_of_study,
                   p.programme_name
            FROM students s
            LEFT JOIN programmes p ON s.programme_id = p.programme_id
            WHERE s.student_id = %s
        """, (student_id,))
        student = cursor.fetchone()

        # Get all published results grouped with year info
        cursor.execute("""
            SELECT
                u.unit_code,
                u.unit_name,
                u.credit_hours,
                u.year_of_study,
                u.semester_number,
                r.cat_marks,
                r.exam_marks,
                r.total_marks,
                r.grade,
                r.grade_points,
                r.remarks,
                sem.semester_name,
                sess.academic_year
            FROM results r
            INNER JOIN units u ON r.unit_id = u.unit_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            INNER JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE r.student_id = %s AND r.is_published = 1
            ORDER BY u.year_of_study, u.semester_number, u.unit_code
        """, (student_id,))

        all_results = cursor.fetchall()

        if not all_results:
            return jsonify({
                "success": True,
                "history": [],
                "overall_average": 0,
                "programme_name": student['programme_name'] if student else None
            })

        # Group by year_of_study → semester_number
        from collections import OrderedDict
        years = OrderedDict()
        for row in all_results:
            yr = row['year_of_study'] or 1
            sem = row['semester_number'] or 1
            key = f"Year {yr}"
            sem_key = f"Semester {sem}"

            if key not in years:
                years[key] = {"year": yr, "label": key, "semesters": OrderedDict(), "all_totals": []}

            if sem_key not in years[key]["semesters"]:
                years[key]["semesters"][sem_key] = {
                    "label": sem_key,
                    "academic_year": row['academic_year'],
                    "units": [],
                    "totals": []
                }

            sem_data = years[key]["semesters"][sem_key]
            total = float(row['total_marks']) if row['total_marks'] else 0
            sem_data["units"].append({
                "unit_code": row['unit_code'],
                "unit_name": row['unit_name'],
                "credit_hours": row['credit_hours'],
                "cat_marks": float(row['cat_marks']) if row['cat_marks'] else None,
                "exam_marks": float(row['exam_marks']) if row['exam_marks'] else None,
                "total_marks": total,
                "grade": row['grade'],
                "remarks": row['remarks'] or ''
            })
            sem_data["totals"].append(total)
            years[key]["all_totals"].append(total)

        # Calculate averages and convert to list
        history = []
        all_totals = []
        for yr_key, yr_data in years.items():
            yr_avg = round(sum(yr_data['all_totals']) / len(yr_data['all_totals']), 1) if yr_data['all_totals'] else 0
            all_totals.extend(yr_data['all_totals'])

            semesters = []
            for sem_key, sem_data in yr_data["semesters"].items():
                sem_avg = round(sum(sem_data['totals']) / len(sem_data['totals']), 1) if sem_data['totals'] else 0
                semesters.append({
                    "label": sem_data['label'],
                    "academic_year": sem_data['academic_year'],
                    "units": sem_data['units'],
                    "average": sem_avg
                })

            history.append({
                "year": yr_data['year'],
                "label": yr_key,
                "semesters": semesters,
                "year_average": yr_avg
            })

        overall_average = round(sum(all_totals) / len(all_totals), 1) if all_totals else 0

        return jsonify({
            "success": True,
            "history": history,
            "overall_average": overall_average,
            "programme_name": student['programme_name'] if student else None
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()
