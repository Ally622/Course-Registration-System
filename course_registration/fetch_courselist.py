from flask import jsonify
from app import app
from db import get_connection

@app.route('/fetch-courses', methods=['GET'])
def fetch_course_list():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT
            course_id,
            course_code,
            course_name,
            credit_hours
        FROM courses
        ORDER BY course_code ASC
        """

        cursor.execute(query)

        courses = cursor.fetchall()

        return jsonify({
            "success": True,
            "courses": courses
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()