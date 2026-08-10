"""
Database connection helper.

Reads credentials from config.py so nothing is hardcoded.
Every route calls get_connection(), uses it, then closes it.
"""

import mysql.connector
from config import Config


def get_connection():
    """
    Create and return a new MySQL connection.

    Returns:
        mysql.connector.connection — an open database connection.

    Raises:
        mysql.connector.Error — if the database is unreachable.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return connection

    except mysql.connector.Error as err:
        print(f"[DB ERROR] Could not connect to MySQL: {err}")
        raise