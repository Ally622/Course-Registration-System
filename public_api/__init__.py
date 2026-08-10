"""
Public API Blueprint — Public endpoints for landing page, schools, etc.
"""

from flask import Blueprint

public_api_bp = Blueprint('public_api', __name__)

from public_api import routes
