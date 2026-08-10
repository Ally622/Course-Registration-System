"""
Admission workflow routes.

Flow:
  Register → Academic Info → KCSE Grades → Programme Selection
  → Submit Application → Admin Approves → Reg Number Generated
  → Student logs in with reg number → Dashboard
"""

from flask import request, jsonify, session
from admission import admission_bp
from db import get_connection
from auth.decorators import login_required


# ============================================================
# Allowed KCSE grades and subjects
# ============================================================
KCSE_GRADES = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']

KCSE_SUBJECTS = [
    'Mathematics', 'English', 'Kiswahili',
    'Biology', 'Chemistry', 'Physics',
    'History & Government', 'Geography', 'Christian Religious Education',
    'Islamic Religious Education', 'Hindu Religious Education',
    'Business Studies', 'Agriculture', 'Computer Studies',
    'Home Science', 'Art & Design', 'Music', 'French', 'German',
    'Arabic', 'Aviation Technology', 'Woodwork Technology',
    'Building Construction', 'Metal Work Technology',
    'Drawing & Design', 'Electricity',
]


# ============================================================
# GET /admission/status — check where the student is in the workflow
# ============================================================
@admission_bp.route('/admission/status', methods=['GET'])
@login_required
def get_status():
    """
    Returns the student's current admission state so the frontend
    knows which step to show.

    Response fields:
      has_kcse_info       — bool
      has_kcse_grades     — bool
      has_application     — bool
      application_status  — 'pending' | 'approved' | 'rejected' | None
      registration_number — str | None
      is_approved         — bool  (shortcut)
    """
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"success": False, "message": "Not a student session."}), 403

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # KCSE info
        cursor.execute(
            "SELECT student_id FROM kcse_info WHERE student_id = %s",
            (student_id,)
        )
        has_kcse_info = cursor.fetchone() is not None

        # KCSE grades count
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM kcse_grades WHERE student_id = %s",
            (student_id,)
        )
        has_kcse_grades = cursor.fetchone()['cnt'] > 0

        # Application
        cursor.execute("""
            SELECT a.status, s.registration_number, a.programme_id
            FROM applications a
            INNER JOIN students s ON a.student_id = s.student_id
            WHERE a.student_id = %s
            ORDER BY a.applied_at DESC
            LIMIT 1
        """, (student_id,))
        app_row = cursor.fetchone()

        has_application = app_row is not None
        application_status = app_row['status'] if app_row else None
        registration_number = app_row['registration_number'] if app_row else None
        is_approved = application_status == 'approved'

        return jsonify({
            "success": True,
            "has_kcse_info": has_kcse_info,
            "has_kcse_grades": has_kcse_grades,
            "has_application": has_application,
            "application_status": application_status,
            "registration_number": registration_number,
            "is_approved": is_approved
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ============================================================
# POST /admission/academic-info — save KCSE exam year / mean grade
# ============================================================
@admission_bp.route('/admission/academic-info', methods=['POST'])
@login_required
def save_academic_info():
    """
    Upsert KCSE info for the logged-in student.

    Expects JSON:
    { "kcse_year": 2023, "index_number": "12345678901/2023", "mean_grade": "B+" }
    """
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"success": False, "message": "Not a student session."}), 403

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400

    kcse_year = data.get("kcse_year")
    index_number = data.get("index_number", "").strip() or None
    mean_grade = data.get("mean_grade", "").strip()

    if not kcse_year or not mean_grade:
        return jsonify({"success": False, "message": "KCSE year and mean grade are required."}), 400

    if mean_grade not in KCSE_GRADES:
        return jsonify({"success": False, "message": f"Invalid mean grade. Allowed: {', '.join(KCSE_GRADES)}"}), 400

    try:
        kcse_year = int(kcse_year)
        if kcse_year < 1990 or kcse_year > 2030:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid KCSE year."}), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO kcse_info (student_id, kcse_year, index_number, mean_grade)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                kcse_year    = VALUES(kcse_year),
                index_number = VALUES(index_number),
                mean_grade   = VALUES(mean_grade)
        """, (student_id, kcse_year, index_number, mean_grade))
        connection.commit()

        return jsonify({"success": True, "message": "Academic information saved."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ============================================================
# GET /admission/academic-info — retrieve saved KCSE info
# ============================================================
@admission_bp.route('/admission/academic-info', methods=['GET'])
@login_required
def get_academic_info():
    student_id = session.get('student_id')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT kcse_year, index_number, mean_grade FROM kcse_info WHERE student_id = %s",
            (student_id,)
        )
        row = cursor.fetchone()
        return jsonify({"success": True, "info": row})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ============================================================
# POST /admission/kcse-grades — save individual subject grades
# ============================================================
@admission_bp.route('/admission/kcse-grades', methods=['POST'])
@login_required
def save_kcse_grades():
    """
    Save KCSE subject grades.

    Expects JSON:
    { "grades": { "Mathematics": "A", "English": "B+", ... } }

    Upserts each (student, subject) pair.
    """
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"success": False, "message": "Not a student session."}), 403

    data = request.get_json()
    grades = data.get("grades", {}) if data else {}

    if not grades:
        return jsonify({"success": False, "message": "No grades provided."}), 400

    # Validate all grades before touching the DB
    for subject, grade in grades.items():
        if subject not in KCSE_SUBJECTS:
            return jsonify({"success": False, "message": f"Unknown subject: {subject}"}), 400
        if grade not in KCSE_GRADES:
            return jsonify({"success": False, "message": f"Invalid grade '{grade}' for {subject}."}), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        for subject, grade in grades.items():
            cursor.execute("""
                INSERT INTO kcse_grades (student_id, subject, grade)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE grade = VALUES(grade)
            """, (student_id, subject, grade))
        connection.commit()

        return jsonify({"success": True, "message": f"{len(grades)} grade(s) saved."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ============================================================
# GET /admission/kcse-grades — retrieve saved grades
# ============================================================
@admission_bp.route('/admission/kcse-grades', methods=['GET'])
@login_required
def get_kcse_grades():
    student_id = session.get('student_id')
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT subject, grade FROM kcse_grades WHERE student_id = %s ORDER BY subject",
            (student_id,)
        )
        rows = cursor.fetchall()
        # Convert list to dict for easy frontend use
        grades = {r['subject']: r['grade'] for r in rows}
        return jsonify({"success": True, "grades": grades, "subjects": KCSE_SUBJECTS, "allowed_grades": KCSE_GRADES})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ============================================================
# GET /admission/programmes — list programmes grouped by school
# ============================================================
@admission_bp.route('/admission/programmes', methods=['GET'])
@login_required
def list_programmes():
    """
    Returns all programmes organised by school.
    Each programme shows: name, description, department, school.
    Does NOT expose lecturer, credits, or unit codes.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    connection = None
    cursor = None
    
    try:
        student_id = session.get('student_id')
        logger.info(f"Student {student_id} requesting programmes list")
        
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT
                p.programme_id,
                p.programme_name,
                p.programme_code,
                p.description,
                p.duration_years,
                d.department_name,
                d.department_id,
                s.school_id,
                s.school_name
            FROM programmes p
            INNER JOIN departments d ON p.department_id = d.department_id
            INNER JOIN schools s ON d.school_id = s.school_id
            WHERE p.is_active = 1
            ORDER BY s.school_name, d.department_name, p.programme_name
        """)
        rows = cursor.fetchall()
        
        logger.info(f"Found {len(rows)} active programmes")

        # Group by school
        from collections import OrderedDict
        grouped = OrderedDict()
        for r in rows:
            sname = r['school_name']
            if sname not in grouped:
                grouped[sname] = {'school_id': r['school_id'], 'school_name': sname, 'programmes': []}
            grouped[sname]['programmes'].append({
                'programme_id': r['programme_id'],
                'programme_name': r['programme_name'],
                'programme_code': r['programme_code'],
                'description': r['description'] or 'A comprehensive programme designed to equip students with essential skills and knowledge.',
                'duration_years': r['duration_years'],
                'department_name': r['department_name'],
                'department_id': r['department_id'],
            })

        result = list(grouped.values())
        logger.info(f"Returning {len(result)} schools with programmes to student {student_id}")
        
        return jsonify({"success": True, "schools": result, "total_programmes": len(rows)})

    except Exception as e:
        logger.error(f"Error fetching programmes for admission: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Failed to load programmes: {str(e)}"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ============================================================
# POST /admission/apply — submit application
# ============================================================
@admission_bp.route('/admission/apply', methods=['POST'])
@login_required
def apply():
    """
    Submit programme application.

    Expects JSON: { "programme_id": 3 }

    Prevents duplicate pending/approved applications.
    Notifies the admin.
    """
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"success": False, "message": "Not a student session."}), 403

    data = request.get_json()
    programme_id = data.get("programme_id") if data else None

    if not programme_id:
        return jsonify({"success": False, "message": "Programme selection is required."}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check programme exists
        cursor.execute("SELECT programme_id, programme_name FROM programmes WHERE programme_id = %s", (programme_id,))
        prog = cursor.fetchone()
        if not prog:
            return jsonify({"success": False, "message": "Programme not found."}), 404

        # Check for existing active application
        cursor.execute("""
            SELECT application_id, status FROM applications
            WHERE student_id = %s AND status IN ('pending', 'approved')
        """, (student_id,))
        existing = cursor.fetchone()
        if existing:
            if existing['status'] == 'approved':
                return jsonify({"success": False, "message": "Your application has already been approved."}), 409
            return jsonify({"success": False, "message": "You already have a pending application."}), 409

        # Verify KCSE info and at least some grades exist
        cursor.execute("SELECT student_id FROM kcse_info WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "message": "Please complete your academic information first."}), 400

        # Insert application
        cursor.execute("""
            INSERT INTO applications (student_id, programme_id, status)
            VALUES (%s, %s, 'pending')
        """, (student_id, programme_id))

        # Notify admin (user_id = 1 is the seeded super admin)
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message)
            SELECT u.user_id, 'New Application', CONCAT(%s, ' has applied for ', %s)
            FROM users u WHERE u.role IN ('admin', 'registrar') LIMIT 1
        """, (session.get('student_name', 'A student'), prog['programme_name']))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Application submitted successfully. You will be notified once reviewed."
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
