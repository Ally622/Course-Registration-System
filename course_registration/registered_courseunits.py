from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/student/course-units', methods=['GET'])
def course_units():

    student_id = request.args.get("student_id")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""

            SELECT

                c.course_code,

                c.course_name,

                c.credit_hours,

                r.registration_status,

                l.lecturer_name

            FROM registrations r

            INNER JOIN courses c

                ON r.course_id = c.course_id

            INNER JOIN lecturers l

                ON c.lecturer_id = l.lecturer_id

            WHERE r.student_id = %s

            ORDER BY c.course_code

        """, (student_id,))

        units = cursor.fetchall()

        return jsonify(units)

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }),500

    finally:

        cursor.close()

        connection.close()