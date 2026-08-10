from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/register-single-course', methods=['POST'])
def register_single_course():

    data = request.get_json()

    student_id = data["student_id"]
    course_id = data["course_id"]

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    check_query = """
    SELECT *
    FROM registrations
    WHERE student_id = %s
    AND course_id = %s
    """

    cursor.execute(check_query, (student_id, course_id))

    existing = cursor.fetchone()

    if existing:

        cursor.close()
        connection.close()

        return jsonify({
            "success": False,
            "message": "Course already registered."
        })

    insert_query = """
    INSERT INTO registrations(student_id, course_id)
    VALUES(%s, %s)
    """

    cursor.execute(insert_query, (student_id, course_id))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Course registered successfully."
    })