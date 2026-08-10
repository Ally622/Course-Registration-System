from flask import jsonify
from app import app
from db import get_connection

@app.route('/registered-courses/<int:student_id>', methods=['GET'])
def registered_courses(student_id):

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        courses.course_code,
        courses.course_name,
        courses.credit_hours
    FROM registrations
    JOIN courses
        ON registrations.course_id = courses.course_id
    WHERE registrations.student_id = %s
    """

    cursor.execute(query, (student_id,))

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(courses)