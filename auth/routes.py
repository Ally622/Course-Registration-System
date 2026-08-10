"""
Auth routes — login, register, forgot password, reset password, logout.

WHAT CHANGED (Auth Flow Refactor):
- Registration no longer requires a registration_number.
  Students register with name, email, phone, and password.
  registration_number is assigned automatically by admin approval.
- Login accepts a unified 'identifier' field — works with either
  email (pre-approval) or registration_number (post-approval).
- /auth/me returns a requires_course_registration flag so the
  frontend can redirect new students to course registration.
"""

import secrets
from datetime import datetime, timedelta

from flask import request, jsonify, session

from auth import auth_bp
from db import get_connection
from extensions import bcrypt
from config import Config


# =============================================================
# POST /auth/login
# =============================================================
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authenticate a user (student, admin, lecturer, or registrar).

    Expects JSON: { "identifier": "...", "password": "..." }
    identifier = email (pre-approval / staff) OR registration_number (post-approval)

    Sets session variables on success.
    """
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    password = data.get("password", "").strip()

    # Accept unified 'identifier' field, or legacy 'email'/'registration_number'
    identifier = data.get("identifier", "").strip()
    if not identifier:
        identifier = data.get("email", "").strip() or data.get("registration_number", "").strip()

    if not password or not identifier:
        return jsonify({
            "success": False,
            "message": "Please provide credentials."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        user = None

        # Strategy: try matching as registration_number first, then email
        # 1) Try as registration number (student with approved reg number)
        cursor.execute("""
            SELECT u.user_id, u.email, u.password_hash, u.role, u.is_active,
                   s.student_id, s.student_name, s.registration_number
            FROM users u
            INNER JOIN students s ON u.user_id = s.user_id
            WHERE s.registration_number = %s
        """, (identifier,))
        user = cursor.fetchone()

        # 2) If not found, try as email (works for all roles)
        if not user:
            cursor.execute("""
                SELECT u.user_id, u.email, u.password_hash, u.role, u.is_active
                FROM users u
                WHERE u.email = %s
            """, (identifier,))
            user = cursor.fetchone()

            # If this is a student with an assigned reg number, reject email login
            if user and user['role'] == 'student':
                cursor.execute("""
                    SELECT student_id, student_name, registration_number
                    FROM students WHERE user_id = %s
                """, (user['user_id'],))
                student_row = cursor.fetchone()
                if student_row:
                    if student_row['registration_number']:
                        # Student has a reg number — must use it, not email
                        return jsonify({
                            "success": False,
                            "message": "Your registration number has been assigned. "
                                       "Please log in using your registration number."
                        }), 401
                    # Student without reg number — email login is OK
                    user['student_id'] = student_row['student_id']
                    user['student_name'] = student_row['student_name']
                    user['registration_number'] = student_row['registration_number']

        # Validate credentials
        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid credentials."
            }), 401

        if not user['is_active']:
            return jsonify({
                "success": False,
                "message": "Account is deactivated. Contact admin."
            }), 403

        if not bcrypt.check_password_hash(user['password_hash'], password):
            return jsonify({
                "success": False,
                "message": "Invalid credentials."
            }), 401

        # --- Login successful — create session ---
        session.permanent = True
        session['user_id'] = user['user_id']
        session['role'] = user['role']

        # Build response based on role
        if user['role'] == 'student':
            session['student_id'] = user['student_id']
            session['student_name'] = user['student_name']
            session['registration_number'] = user.get('registration_number')

            # Check if student needs course registration (no approved courses)
            requires_course_registration = False
            cursor.execute("""
                SELECT COUNT(*) AS cnt FROM registrations
                WHERE student_id = %s AND status IN ('pending', 'approved')
            """, (user['student_id'],))
            reg_count = cursor.fetchone()['cnt']
            if reg_count == 0:
                requires_course_registration = True

            # Log the login action
            _log_action(cursor, user['user_id'], 'LOGIN', 'users', user['user_id'],
                        f"Student {user['student_name']} logged in")

            connection.commit()

            return jsonify({
                "success": True,
                "message": "Login successful.",
                "user": {
                    "user_id": user['user_id'],
                    "student_id": user['student_id'],
                    "name": user['student_name'],
                    "registration_number": user.get('registration_number'),
                    "role": "student",
                    "requires_course_registration": requires_course_registration
                }
            })

        elif user['role'] == 'admin':
            # Fetch admin details
            cursor.execute("""
                SELECT admin_id, admin_name, role_level
                FROM admins
                WHERE user_id = %s
            """, (user['user_id'],))
            admin = cursor.fetchone()

            session['admin_id'] = admin['admin_id'] if admin else None
            session['admin_name'] = admin['admin_name'] if admin else 'Admin'

            _log_action(cursor, user['user_id'], 'LOGIN', 'users', user['user_id'],
                        f"Admin {session['admin_name']} logged in")
            connection.commit()

            return jsonify({
                "success": True,
                "message": "Login successful.",
                "user": {
                    "user_id": user['user_id'],
                    "admin_id": session['admin_id'],
                    "name": session['admin_name'],
                    "role": "admin"
                }
            })

        elif user['role'] == 'lecturer':
            # Fetch lecturer details
            cursor.execute("""
                SELECT lecturer_id, lecturer_name, department_id
                FROM lecturers
                WHERE user_id = %s
            """, (user['user_id'],))
            lecturer = cursor.fetchone()

            session['lecturer_id'] = lecturer['lecturer_id'] if lecturer else None
            session['lecturer_name'] = lecturer['lecturer_name'] if lecturer else 'Lecturer'

            _log_action(cursor, user['user_id'], 'LOGIN', 'users', user['user_id'],
                        f"Lecturer {session['lecturer_name']} logged in")
            connection.commit()

            return jsonify({
                "success": True,
                "message": "Login successful.",
                "user": {
                    "user_id": user['user_id'],
                    "lecturer_id": session['lecturer_id'],
                    "name": session['lecturer_name'],
                    "role": "lecturer"
                }
            })

        elif user['role'] == 'registrar':
            # Fetch admin record (registrars also stored in admins table)
            cursor.execute("""
                SELECT admin_id, admin_name
                FROM admins
                WHERE user_id = %s
            """, (user['user_id'],))
            registrar = cursor.fetchone()

            session['admin_id'] = registrar['admin_id'] if registrar else None
            session['admin_name'] = registrar['admin_name'] if registrar else 'Registrar'

            _log_action(cursor, user['user_id'], 'LOGIN', 'users', user['user_id'],
                        f"Registrar {session['admin_name']} logged in")
            connection.commit()

            return jsonify({
                "success": True,
                "message": "Login successful.",
                "user": {
                    "user_id": user['user_id'],
                    "admin_id": session.get('admin_id'),
                    "name": session['admin_name'],
                    "role": "registrar"
                }
            })

        else:
            return jsonify({
                "success": False,
                "message": "Unknown role."
            }), 403

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# POST /auth/register
# =============================================================
@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new student account.

    Expects JSON:
    {
        "name": "...",
        "email": "...",
        "phone": "...",
        "password": "..."
    }

    Creates a row in users AND students tables.
    Registration number is NOT set here — it is generated when
    an admin approves the student's course registration.
    """
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    # Extract and validate fields
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    password = data.get("password", "").strip()

    if not all([name, email, password]):
        return jsonify({
            "success": False,
            "message": "Name, email, and password are required."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert into users
        cursor.execute("""
            INSERT INTO users (email, password_hash, role)
            VALUES (%s, %s, 'student')
        """, (email, password_hash))

        user_id = cursor.lastrowid

        # Insert into students (registration_number is NULL — assigned on approval)
        cursor.execute("""
            INSERT INTO students (user_id, student_name, phone)
            VALUES (%s, %s, %s)
        """, (user_id, name, phone))

        # Log the registration
        _log_action(cursor, user_id, 'REGISTER', 'users', user_id,
                    f"New student registered: {name} ({email})")

        # --- Auto-login the user immediately after registration ---
        cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (user_id,))
        student_row = cursor.fetchone()
        
        session.permanent = True
        session['user_id'] = user_id
        session['role'] = 'student'
        if student_row:
            session['student_id'] = student_row['student_id']
            session['student_name'] = name
            session['registration_number'] = None

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful. You are now logged in.",
            "user": {
                "user_id": user_id,
                "student_id": session.get('student_id'),
                "name": name,
                "role": "student"
            }
        }), 201

    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================================================
# POST /auth/forgot-password
# =============================================================
@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """
    Generate a password reset token for a user.

    Expects JSON: { "email": "..." }
    Returns a token that can be used with /auth/reset-password.
    """
    data = request.get_json()
    email = data.get("email", "").strip() if data else ""

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            # Don't reveal whether email exists (security best practice)
            return jsonify({
                "success": True,
                "message": "If the email exists, reset instructions have been sent."
            })

        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(
            hours=Config.PASSWORD_RESET_EXPIRY_HOURS
        )

        # Invalidate any existing tokens for this user
        cursor.execute(
            "UPDATE password_reset_tokens SET used = 1 WHERE user_id = %s",
            (user['user_id'],)
        )

        # Save new token
        cursor.execute("""
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        """, (user['user_id'], token, expires_at))

        # Log the action
        _log_action(cursor, user['user_id'], 'FORGOT_PASSWORD', 'password_reset_tokens',
                    None, f"Password reset token generated for {email}")

        connection.commit()

        # In production, you would send this token via email.
        # For development, we return it directly.
        return jsonify({
            "success": True,
            "message": "Password reset token generated.",
            "token": token  # Remove this line in production
        })

    except Exception as e:
        connection.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# POST /auth/reset-password
# =============================================================
@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using a valid token.

    Expects JSON: { "token": "...", "new_password": "..." }
    """
    data = request.get_json()
    token = data.get("token", "").strip() if data else ""
    new_password = data.get("new_password", "").strip() if data else ""

    if not token or not new_password:
        return jsonify({
            "success": False,
            "message": "Token and new password are required."
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Find valid (unused, not expired) token
        cursor.execute("""
            SELECT user_id
            FROM password_reset_tokens
            WHERE token = %s
              AND used = 0
              AND expires_at > NOW()
        """, (token,))

        token_row = cursor.fetchone()

        if not token_row:
            return jsonify({
                "success": False,
                "message": "Invalid or expired reset token."
            }), 400

        # Hash new password and update user
        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_hash, token_row['user_id'])
        )

        # Mark token as used
        cursor.execute(
            "UPDATE password_reset_tokens SET used = 1 WHERE token = %s",
            (token,)
        )

        # Log the action
        _log_action(cursor, token_row['user_id'], 'RESET_PASSWORD', 'users',
                    token_row['user_id'], 'Password reset via token')

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Password reset successfully. You can now log in."
        })

    except Exception as e:
        connection.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


# =============================================================
# POST /auth/logout
# =============================================================
@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Log out the current user by clearing the session.
    """
    user_id = session.get('user_id')

    # Log the logout action before clearing session
    if user_id:
        try:
            connection = get_connection()
            cursor = connection.cursor()
            _log_action(cursor, user_id, 'LOGOUT', 'users', user_id, 'User logged out')
            connection.commit()
            cursor.close()
            connection.close()
        except Exception:
            pass  # Don't fail logout if logging fails

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# =============================================================
# GET /auth/me — check current session
# =============================================================
@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """
    Return the currently logged-in user's info from the session.
    Useful for the frontend to check auth status on page load.
    """
    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "logged_in": False,
            "message": "Not logged in."
        }), 401

    return jsonify({
        "success": True,
        "logged_in": True,
        "user": {
            "user_id": session['user_id'],
            "role": session['role'],
            "student_id": session.get('student_id'),
            "student_name": session.get('student_name'),
            "registration_number": session.get('registration_number'),
            "admin_id": session.get('admin_id'),
            "admin_name": session.get('admin_name'),
            "lecturer_id": session.get('lecturer_id'),
            "lecturer_name": session.get('lecturer_name'),
            # name alias — used by populateNavbar on the frontend
            "name": (
                session.get('student_name') or
                session.get('admin_name') or
                session.get('lecturer_name') or
                'User'
            )
        }
    })


# =============================================================
# HELPER: Audit logging
# =============================================================
def _log_action(cursor, user_id, action, table_name=None, record_id=None, new_value=None):
    """
    Insert an audit log entry.

    This is a helper called internally by auth routes.
    Uses the cursor from the calling function so the log
    is committed with the same transaction.

    Args:
        cursor:     Active database cursor.
        user_id:    ID of the user performing the action.
        action:     Action name (e.g. 'LOGIN', 'REGISTER').
        table_name: Name of the affected table.
        record_id:  ID of the affected record.
        new_value:  Description of the change.
    """
    try:
        # FIX: Use correct table name 'system_logs' and column 'description'
        cursor.execute("""
            INSERT INTO system_logs (user_id, action, table_name, record_id, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, action, table_name, record_id, new_value))
    except Exception as e:
        # Log the error for debugging but don't break the main operation
        print(f"Warning: Failed to write audit log: {str(e)}")
        pass
