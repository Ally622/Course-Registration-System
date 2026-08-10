"""
Auth decorators — reusable access control for all routes.

Usage:
    @login_required
    def some_student_route():
        ...

    @admin_required
    def some_admin_route():
        ...

    @role_required('admin', 'registrar')
    def some_restricted_route():
        ...

    @lecturer_required
    def some_lecturer_route():
        ...
"""

from functools import wraps
from flask import session, jsonify


def login_required(f):
    """
    Decorator that blocks unauthenticated users.

    Checks that session contains a valid user_id.
    Returns 401 if not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "message": "Login required. Please sign in."
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator that blocks non-admin users.

    Allows both 'admin' and 'registrar' roles — registrars need full
    access to registration management and course admin pages.
    Returns 403 for students and lecturers.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "message": "Login required. Please sign in."
            }), 401

        if session.get('role') not in ('admin', 'registrar'):
            return jsonify({
                "success": False,
                "message": "Admin access required."
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def lecturer_required(f):
    """
    Decorator that blocks non-lecturer users.

    Checks that session contains role == 'lecturer'.
    Returns 403 if not a lecturer.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "message": "Login required. Please sign in."
            }), 401

        if session.get('role') != 'lecturer':
            return jsonify({
                "success": False,
                "message": "Lecturer access required."
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def registrar_required(f):
    """
    Decorator that blocks non-registrar users.

    Checks that session contains role == 'registrar'.
    Returns 403 if not a registrar.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                "success": False,
                "message": "Login required. Please sign in."
            }), 401

        if session.get('role') != 'registrar':
            return jsonify({
                "success": False,
                "message": "Registrar access required."
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    Flexible decorator that restricts access to specific roles.

    Usage:
        @role_required('admin', 'registrar')
        def manage_registrations():
            ...

    Args:
        *roles: One or more role strings ('admin', 'student',
                'lecturer', 'registrar').

    Returns 401 if not logged in, 403 if role doesn't match.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({
                    "success": False,
                    "message": "Login required. Please sign in."
                }), 401

            user_role = session.get('role')
            if user_role not in roles:
                return jsonify({
                    "success": False,
                    "message": f"Access denied. Required role(s): {', '.join(roles)}."
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
