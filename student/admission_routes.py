from flask import Blueprint, request, jsonify, session
from db import get_connection
from auth.decorators import login_required, role_required

admission_bp = Blueprint('admission', __name__)

@admission_bp.route('/student/kcse', methods=['POST'])
@login_required
@role_required('student')
def submit_kcse_info():
    """Submit KCSE info and grades."""
    student_id = session.get('student_id')
    data = request.get_json()

    kcse_year = data.get('kcse_year')
    index_number = data.get('index_number')
    mean_grade = data.get('mean_grade')
    grades = data.get('grades')  # dictionary { "English": "B+", ... }

    if not all([kcse_year, mean_grade, grades]):
        return jsonify({"success": False, "message": "Missing required KCSE info or grades."}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if already submitted
        cursor.execute("SELECT student_id FROM kcse_info WHERE student_id = %s", (student_id,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "KCSE info already submitted."}), 400

        # Insert info
        cursor.execute("""
            INSERT INTO kcse_info (student_id, kcse_year, index_number, mean_grade)
            VALUES (%s, %s, %s, %s)
        """, (student_id, kcse_year, index_number, mean_grade))

        # Insert grades
        for subject, grade in grades.items():
            if grade: # Only insert if a grade was selected
                cursor.execute("""
                    INSERT INTO kcse_grades (student_id, subject, grade)
                    VALUES (%s, %s, %s)
                """, (student_id, subject, grade))

        connection.commit()

        return jsonify({"success": True, "message": "KCSE info saved successfully."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@admission_bp.route('/student/programmes', methods=['GET'])
@login_required
@role_required('student')
def get_programmes():
    """Fetch all programmes grouped by school."""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT p.programme_id, p.programme_name, p.description, 
                   d.department_name, s.school_name
            FROM programmes p
            INNER JOIN departments d ON p.department_id = d.department_id
            INNER JOIN schools s ON d.school_id = s.school_id
            ORDER BY s.school_name, p.programme_name
        """)
        programmes = cursor.fetchall()

        # Group by school
        grouped = {}
        for p in programmes:
            school = p['school_name']
            if school not in grouped:
                grouped[school] = []
            grouped[school].append({
                "programme_id": p['programme_id'],
                "programme_name": p['programme_name'],
                "department_name": p['department_name'],
                "description": p['description']
            })

        # Format as list for easier frontend parsing
        result = [{"school_name": k, "programmes": v} for k, v in grouped.items()]

        return jsonify({"success": True, "schools": result})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@admission_bp.route('/student/apply', methods=['POST'])
@login_required
@role_required('student')
def apply_programme():
    """Submit an application for a specific programme."""
    student_id = session.get('student_id')
    user_id = session.get('user_id')
    data = request.get_json()
    programme_id = data.get('programme_id')

    if not programme_id:
        return jsonify({"success": False, "message": "Programme ID is required."}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if already applied
        cursor.execute("SELECT status FROM applications WHERE student_id = %s", (student_id,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"success": False, "message": f"You already have an application with status: {existing['status']}."}), 400

        # Insert application
        cursor.execute("""
            INSERT INTO applications (student_id, programme_id, status)
            VALUES (%s, %s, 'pending')
        """, (student_id, programme_id))
        
        # Log and notify
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message)
            VALUES (%s, %s, %s)
        """, (user_id, 'Application Submitted', 'Your programme application has been submitted successfully and is pending admin approval.'))

        connection.commit()

        return jsonify({"success": True, "message": "Your application has been submitted successfully. Please wait for approval. A registration number will be generated after approval."})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
