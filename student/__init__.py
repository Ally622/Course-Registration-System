"""
Student Blueprint — dashboard, profile, results, timetable.

Preserves all existing route logic from dashboard.py, profile.py,
results.py, and timetable.py while adding missing features.
"""

from flask import Blueprint

student_bp = Blueprint('student', __name__)

from student import routes  # noqa: E402, F401
