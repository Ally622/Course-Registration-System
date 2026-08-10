from flask import Flask, request, jsonify, render_template
from db import get_connection

app = Flask(__name__)

@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM users
    WHERE username = %s
    """

    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user and user["password"] == password:
        return jsonify({
            "success": True,
            "message": "Login Successful"
        })

    return jsonify({
        "success": False,
        "message": "Invalid Username or Password"
    })


if __name__ == "__main__":
    app.run(debug=True)