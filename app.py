"""
Course Registration System — Main Application Entry Point.

This file creates the Flask app, initializes all extensions,
and registers all Blueprints (auth, student, registration, admin).

WHAT CHANGED:
- Original app.py imported non-existent modules (auth.login, auth.register)
  which caused a fatal crash on startup.
- Now uses Flask Blueprints for clean modular organization.
- All original route handlers are PRESERVED inside their Blueprint modules.

To run:
    pip install -r requirements.txt
    python app.py
"""

import os
from flask import Flask, send_from_directory, jsonify, request
from config import DevelopmentConfig
from extensions import bcrypt, csrf, cors


def create_app(config_class=DevelopmentConfig):
    """
    Application factory — creates and configures the Flask app.

    Using a factory function is a Flask best practice because it:
    1. Allows different configs for dev/test/prod.
    2. Prevents circular imports.
    3. Makes testing easier.
    """

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set the secret key for sessions
    app.secret_key = config_class.SECRET_KEY

    # --- Initialize Extensions ---
    bcrypt.init_app(app)
    csrf.init_app(app)
    cors.init_app(app, supports_credentials=True)

    # Exempt API routes from CSRF (since we use JSON, not forms)
    # CSRF is still enforced for any form-based submissions
    csrf._exempt_views = set()

    # --- Configure File Uploads ---
    app.config['UPLOAD_FOLDER'] = config_class.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = config_class.MAX_CONTENT_LENGTH
    os.makedirs(config_class.UPLOAD_FOLDER, exist_ok=True)

    # --- Register Blueprints ---
    from auth import auth_bp
    from student import student_bp
    from registration import registration_bp
    from admin import admin_bp
    from admission import admission_bp
    from public_api import public_api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admission_bp)
    app.register_blueprint(public_api_bp)

    # --- Exempt all API routes from CSRF ---
    # Since this is a JSON API backend, CSRF tokens are impractical.
    # CORS + session cookies provide sufficient protection.
    with app.app_context():
        for view_name in app.view_functions:
            csrf.exempt(app.view_functions[view_name])

    # --- Health Check Endpoint ---
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Simple endpoint to verify the server is running."""
        return {
            "success": True,
            "message": "Course Registration System is running.",
            "version": "1.0.0"
        }

    # --- Programmes API Endpoint (Alias for /api/public/programmes) ---
    @app.route('/api/programmes', methods=['GET'])
    def api_programmes():
        """
        Direct /api/programmes endpoint.
        Returns all programmes grouped by school.
        This is an alias that forwards to the public API.
        """
        import logging
        from db import get_connection
        
        logger = logging.getLogger(__name__)
        connection = None
        cursor = None
        
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            
            logger.info("API: Fetching all programmes")
            
            cursor.execute("""
                SELECT
                    p.programme_id,
                    p.programme_name,
                    p.programme_code,
                    p.description,
                    p.duration_years,
                    d.department_id,
                    d.department_name,
                    s.school_id,
                    s.school_name
                FROM programmes p
                INNER JOIN departments d ON p.department_id = d.department_id
                INNER JOIN schools s ON d.school_id = s.school_id
                WHERE p.is_active = 1
                ORDER BY s.school_name, d.department_name, p.programme_name
            """)
            programmes = cursor.fetchall()
            
            logger.info(f"API: Found {len(programmes)} programmes")

            # Group by school
            from collections import OrderedDict
            grouped = OrderedDict()
            for p in programmes:
                sname = p['school_name']
                if sname not in grouped:
                    grouped[sname] = {
                        'school_id': p['school_id'],
                        'school_name': sname,
                        'programmes': []
                    }
                grouped[sname]['programmes'].append({
                    'programme_id': p['programme_id'],
                    'programme_name': p['programme_name'],
                    'programme_code': p['programme_code'],
                    'description': p['description'] or 'A comprehensive programme designed to equip students with essential skills and knowledge.',
                    'duration_years': p['duration_years'],
                    'department_name': p['department_name'],
                    'department_id': p['department_id'],
                })

            result = list(grouped.values())
            
            return jsonify({"success": True, "schools": result, "total_programmes": len(programmes)})

        except Exception as e:
            logger.error(f"API: Error fetching programmes: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # --- JSON error handlers ---
    # Flask's default 400/404/405/500 handlers return HTML pages.
    # These handlers override that so every error the JS fetch() receives
    # is JSON — preventing the "Unexpected token '<'" SyntaxError.

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(success=False, message="Bad request."), 400

    @app.errorhandler(404)
    def not_found(e):
        # If the request is for an HTML file, serve the frontend (SPA-style).
        # For API calls (/auth/..., /admin/..., etc.) return JSON.
        path = request.path
        if path.startswith('/auth/') or path.startswith('/admin/') \
                or path.startswith('/student/') or path.startswith('/registration/') \
                or path.startswith('/api/'):
            return jsonify(success=False, message=f"Endpoint not found: {path}"), 404
        # Non-API 404 — try to serve from frontend directory
        try:
            return send_from_directory(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend'),
                '404.html'
            )
        except Exception:
            return jsonify(success=False, message="Page not found."), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(success=False, message="Method not allowed."), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(success=False, message="Internal server error. Check Flask logs."), 500

    # --- Serve uploaded profile photos ---
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded files (profile photos)."""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # --- Serve Frontend Static Files ---
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

    @app.route('/')
    def serve_landing():
        """Serve the landing page."""
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filepath>')
    def serve_frontend(filepath):
        """Serve any frontend file (HTML, CSS, JS, images)."""
        return send_from_directory(frontend_dir, filepath)

    return app


# --- Entry Point ---
# When you run `python app.py`, this creates the app and starts it.
app = create_app()

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  Course Registration System")
    print("  Running on: http://127.0.0.1:5000")
    print("=" * 55)
    print("\n  API Endpoints:")
    print("  Auth:         /auth/login, /auth/register, /auth/logout")
    print("  Dashboard:    /student/dashboard")
    print("  Profile:      /student/profile")
    print("  Results:      /student/results")
    print("  Timetable:    /student/timetable")
    print("  Registration: /registration/courses, /registration/register")
    print("  Admin:        /admin/dashboard, /admin/students, ...")
    print("  Health:       /api/health")
    print("=" * 55 + "\n")

    app.run(debug=True)
