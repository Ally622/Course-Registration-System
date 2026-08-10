from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/register-course', methods=['POST'])
def register_course():

    data = request.get_json()

    student_id = data["student_id"]
    courses = data["courses"]

    connection = get_connection()

    cursor = connection.cursor()

    for course_id in courses:

        query = """
        INSERT INTO registrations(student_id, course_id)
        VALUES(%s, %s)
        """

        cursor.execute(query, (student_id, course_id))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Registration completed successfully."
    })