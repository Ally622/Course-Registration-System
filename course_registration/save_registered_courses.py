from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/save-registration', methods=['POST'])
def save_registration():

    # Receive data from the frontend
    student_id = request.form.get('student_id')
    selected_courses = request.form.getlist('courses')

    # Validate input
    if not student_id or not selected_courses:
        return jsonify({
            "success": False,
            "message": "Student ID or selected courses are missing."
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Save each selected course
        for course_id in selected_courses:

            query = """
            INSERT INTO registrations (student_id, course_id)
            VALUES (%s, %s)
            """

            cursor.execute(query, (student_id, course_id))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Courses registered successfully."
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