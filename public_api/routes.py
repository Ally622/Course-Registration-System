"""
Public API Routes — endpoints that don't require authentication.
Used by the landing page, schools page, and admission forms.
"""

from collections import OrderedDict
from flask import jsonify, request
import logging

from public_api import public_api_bp
from db import get_connection

logger = logging.getLogger(__name__)


# =============================================================
# GET /api/public/programmes — Get all programmes by school
# =============================================================
@public_api_bp.route('/api/public/programmes', methods=['GET'])
def get_programmes():
    """
    Return all active programmes grouped by school.
    Used by the landing page and admission forms.
    """
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        logger.info("Public API: Fetching all programmes")
        
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
        
        logger.info(f"Public API: Found {len(programmes)} programmes")

        # Group by school
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
        
        return jsonify({
            "success": True,
            "schools": result,
            "total_programmes": len(programmes)
        })

    except Exception as e:
        logger.error(f"Public API: Error fetching programmes: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Database error: {str(e)}"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================================================
# GET /api/public/schools — Get all schools
# =============================================================
@public_api_bp.route('/api/public/schools', methods=['GET'])
def get_schools():
    """Return all active schools."""
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT school_id, school_name, description
            FROM schools
            WHERE is_active = 1
            ORDER BY school_name
        """)
        schools = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "schools": schools
        })

    except Exception as e:
        logger.error(f"Public API: Error fetching schools: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================================================
# GET /api/public/departments — Get departments by school
# =============================================================
@public_api_bp.route('/api/public/departments', methods=['GET'])
def get_departments():
    """
    Return departments, optionally filtered by school_id.
    Query param: school_id (optional)
    """
    school_id = request.args.get('school_id', type=int)
    
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if school_id:
            cursor.execute("""
                SELECT
                    d.department_id,
                    d.department_name,
                    d.description,
                    s.school_name
                FROM departments d
                INNER JOIN schools s ON d.school_id = s.school_id
                WHERE d.school_id = %s AND d.is_active = 1
                ORDER BY d.department_name
            """, (school_id,))
        else:
            cursor.execute("""
                SELECT
                    d.department_id,
                    d.department_name,
                    d.description,
                    s.school_name
                FROM departments d
                INNER JOIN schools s ON d.school_id = s.school_id
                WHERE d.is_active = 1
                ORDER BY s.school_name, d.department_name
            """)
        
        departments = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "departments": departments
        })

    except Exception as e:
        logger.error(f"Public API: Error fetching departments: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
