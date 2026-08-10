from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/search-courses', methods=['GET'])
def search_courses():

    # Get search keyword from the frontend
    keyword = request.args.get('keyword', '').strip()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        if keyword:
            query = """
            SELECT
                course_id,
                course_code,
                course_name,
                credit_hours
            FROM courses
            WHERE course_code LIKE %s
               OR course_name LIKE %s
            ORDER BY course_code ASC
            """

            search = f"%{keyword}%"
            cursor.execute(query, (search, search))

        else:
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