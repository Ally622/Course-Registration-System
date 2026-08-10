from flask import jsonify
from app import app
from db import get_connection

@app.route('/courses', methods=['GET'])
def get_courses():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        course_id,
        course_code,
        course_name,
        credit_hours
    FROM courses
    ORDER BY course_code
    """

    cursor.execute(query)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(courses)