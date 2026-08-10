from flask import request, jsonify
from app import app
from db import get_connection

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    name = data["name"]
    email = data["email"]
    password = data["password"]

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO users(name, email, password)
    VALUES(%s, %s, %s)
    """

    cursor.execute(query, (name, email, password))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Registration Successful"
    })