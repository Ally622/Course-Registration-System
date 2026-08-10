"""
Registration Blueprint — course registration, drop, and PDF download.

Consolidates and preserves logic from the original course_registration/ folder.
"""

from flask import Blueprint

registration_bp = Blueprint('registration', __name__)

from registration import routes         # noqa: E402, F401
from registration import pdf_generator  # noqa: E402, F401
