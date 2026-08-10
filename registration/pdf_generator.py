"""
PDF generator for registration forms.

Uses reportlab to create a professional registration form
that students can download.
"""

import io
from datetime import datetime

from flask import session, jsonify, send_file

from registration import registration_bp
from db import get_connection
from auth.decorators import login_required

# reportlab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


@registration_bp.route('/registration/download-pdf', methods=['GET'])
@login_required
def download_registration_pdf():
    """
    Generate and return a PDF registration form for the current student.
    """
    student_id = session.get('student_id')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get student info
        cursor.execute("""
            SELECT
                s.student_name,
                s.registration_number,
                s.year_of_study,
                d.department_name,
                sch.school_name
            FROM students s
            LEFT JOIN departments d   ON s.department_id = d.department_id
            LEFT JOIN schools sch     ON d.school_id     = sch.school_id
            WHERE s.student_id = %s
        """, (student_id,))
        student = cursor.fetchone()

        if not student:
            return jsonify({
                "success": False,
                "message": "Student not found."
            }), 404

        # Get active semester
        cursor.execute("""
            SELECT sem.semester_name, sess.academic_year
            FROM semesters sem
            LEFT JOIN academic_sessions sess ON sem.session_id = sess.session_id
            WHERE sem.is_active = 1
            LIMIT 1
        """)
        semester = cursor.fetchone()

        # Get registered courses
        cursor.execute("""
            SELECT
                c.course_code,
                c.course_name,
                c.credit_hours,
                r.status,
                l.lecturer_name
            FROM registrations r
            INNER JOIN courses c ON r.course_id = c.course_id
            LEFT JOIN lecturers l ON c.lecturer_id = l.lecturer_id
            INNER JOIN semesters sem ON r.semester_id = sem.semester_id
            WHERE r.student_id = %s
              AND sem.is_active = 1
              AND r.status != 'dropped'
            ORDER BY c.course_code
        """, (student_id,))
        courses = cursor.fetchall()

        # --- Build PDF ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        elements = []
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#C2185B'),
            alignment=TA_CENTER,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # Header
        elements.append(Paragraph("Course Registration Form", title_style))
        elements.append(Paragraph(
            f"{semester['semester_name']} — {semester['academic_year']}" if semester else "Current Semester",
            subtitle_style
        ))
        elements.append(Spacer(1, 12))

        # Student info table
        info_data = [
            ["Student Name:", student['student_name']],
            ["Registration No:", student['registration_number']],
            ["Department:", student.get('department_name', 'N/A')],
            ["School:",     student.get('school_name',    'N/A')],
            ["Year of Study:", str(student.get('year_of_study', 'N/A'))],
            ["Date:", datetime.now().strftime('%B %d, %Y')],
        ]

        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # Course table header
        elements.append(Paragraph("Registered Course Units", styles['Heading2']))
        elements.append(Spacer(1, 8))

        course_data = [["#", "Course Code", "Course Name", "Credits", "Lecturer", "Status"]]

        total_credits = 0
        for i, course in enumerate(courses, 1):
            course_data.append([
                str(i),
                course['course_code'],
                course['course_name'],
                str(course['credit_hours']),
                course.get('lecturer_name', 'TBA'),
                course['status'].capitalize()
            ])
            total_credits += course['credit_hours']

        # Total row
        course_data.append(["", "", "Total Credit Hours", str(total_credits), "", ""])

        course_table = Table(
            course_data,
            colWidths=[0.4 * inch, 1.1 * inch, 2.2 * inch, 0.7 * inch, 1.2 * inch, 0.9 * inch]
        )

        course_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C2185B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Body rows
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),

            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FCE4EC')),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#FFF0F5')]),

            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(course_table)
        elements.append(Spacer(1, 40))

        # Signature lines
        sig_data = [
            ["_________________________", "", "_________________________"],
            ["Student Signature", "", "Registrar Signature"],
            ["", "", ""],
            ["Date: ___________________", "", "Date: ___________________"],
        ]

        sig_table = Table(sig_data, colWidths=[2.5 * inch, 1 * inch, 2.5 * inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(sig_table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        filename = f"registration_form_{student['registration_number'].replace('/', '_')}.pdf"

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()
