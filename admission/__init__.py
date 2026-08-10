"""
Admission Blueprint — handles the student admission workflow:
  1. POST /admission/academic-info       — save KCSE year, index, mean grade
  2. POST /admission/kcse-grades         — save per-subject grades
  3. GET  /admission/kcse-grades         — fetch saved grades
  4. GET  /admission/programmes          — list all programmes grouped by school
  5. POST /admission/apply               — submit application
  6. GET  /admission/status              — get application status
"""

from flask import Blueprint

admission_bp = Blueprint('admission', __name__)

from admission import routes  # noqa: E402, F401
