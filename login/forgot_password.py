from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/forgot-password', methods=['POST'])
def forgot_password():

    email = request.form.get("email")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user:

        return jsonify({
            "success": True,
            "message": "Password reset instructions sent."
        })

    return jsonify({
        "success": False,
        "message": "Email not found."
    })