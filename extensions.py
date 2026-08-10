"""
Shared Flask extensions for the Course Registration System.

All extensions are initialized here WITHOUT the app instance,
then attached to the app in app.py using init_app().
This avoids circular imports — a very common Flask problem.
"""

from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

# Password hashing (bcrypt)
bcrypt = Bcrypt()

# CSRF protection for form submissions
csrf = CSRFProtect()

# Cross-Origin Resource Sharing (needed if frontend is separate)
cors = CORS()
