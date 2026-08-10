"""
Configuration module for the Course Registration System.

Centralizes all settings — database, security, file uploads —
so nothing is hardcoded across the codebase.
"""

import os


class Config:
    """Base configuration shared by all environments."""

    # ----- Flask Core -----
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ----- Database (MySQL) -----
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'course_registration_system')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))

    # ----- Session -----
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds

    # ----- File Uploads -----
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'uploads'
    )
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # ----- Credit Limits -----
    MAX_CREDIT_HOURS_PER_SEMESTER = 24
    MIN_CREDIT_HOURS_PER_SEMESTER = 12

    # ----- Password Reset -----
    PASSWORD_RESET_EXPIRY_HOURS = 24


class DevelopmentConfig(Config):
    """Development-specific settings."""
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific settings."""
    DEBUG = False
    # In production, SECRET_KEY MUST come from environment variable
