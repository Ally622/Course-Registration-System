"""
Auth Blueprint — handles login, registration, forgot password, logout.

All existing login logic from the original login/ folder is preserved
and enhanced with password hashing, sessions, and role-based auth.
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Import routes so they register with the blueprint
from auth import routes  # noqa: E402, F401
