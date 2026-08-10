"""
Admin Blueprint — dashboard, manage students/courses/departments/
schools/semesters, approve registrations, reports, and exports.
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from admin import routes   # noqa: E402, F401
from admin import exports  # noqa: E402, F401
