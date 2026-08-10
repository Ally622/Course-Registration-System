# Course Registration System

A complete web-based course registration system built with Flask (Python) and MySQL.

## Features

### Student Portal
- ✅ User registration and authentication
- ✅ Course/Unit browsing and registration
- ✅ View registered courses
- ✅ Check results and GPA
- ✅ View personal timetable
- ✅ Profile management
- ✅ Registration history

### Admin Portal
- ✅ Student management
- ✅ Course/Unit management
- ✅ Registration approval
- ✅ Results management
- ✅ Semester management
- ✅ Reports and analytics

## Quick Start

### Prerequisites
1. **Python 3.8+** installed
2. **MySQL Server** running
3. **pip** (Python package manager)

### Installation Steps

1. **Setup Database**
   ```bash
   # Login to MySQL
   mysql -u root -p
   
   # Create database
   CREATE DATABASE course_registration_system;
   USE course_registration_system;
   
   # Run schema
   SOURCE database/schema.sql;
   
   # Load sample data
   SOURCE database/seed_data.sql;
   ```

2. **Configure Database Connection**
   
   Edit `config.py` if your MySQL settings are different:
   ```python
   DB_HOST = 'localhost'
   DB_USER = 'root'
   DB_PASSWORD = ''  # Your MySQL password
   DB_NAME = 'course_registration_system'
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Database Setup**
   ```bash
   python verify_database.py
   ```

5. **Start the System**
   
   **Option A - Windows:**
   ```bash
   START_SYSTEM.bat
   ```
   
   **Option B - Command Line:**
   ```bash
   python app.py
   ```

6. **Access the System**
   
   Open browser: `http://127.0.0.1:5000`

## Default Login Credentials

### Admin Account
- **Email:** `admin@university.edu`
- **Password:** `admin123`

### Student Account
- **Email:** `john.doe@student.edu`  
  **OR**  
  **Registration Number:** `CS/2026/0001`
- **Password:** `student123`

### Lecturer Account
- **Email:** `jane.smith@university.edu`
- **Password:** `lecturer123`

## Project Structure

```
Course_Registration/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── db.py                  # Database connection
├── extensions.py          # Flask extensions (bcrypt, CSRF, CORS)
├── requirements.txt       # Python dependencies
│
├── auth/                  # Authentication blueprint
│   ├── routes.py         # Login, register, logout endpoints
│   └── decorators.py     # @login_required decorator
│
├── student/               # Student portal blueprint
│   ├── routes.py         # Dashboard, profile, results, timetable
│   └── admission_routes.py
│
├── registration/          # Course registration blueprint
│   ├── routes.py         # Unit registration, viewing, history
│   └── pdf_generator.py  # Registration slip PDF generation
│
├── admin/                 # Admin portal blueprint
│   ├── routes.py         # Student/course/registration management
│   └── exports.py        # Report exports
│
├── admission/             # Admission process blueprint
│   └── routes.py         # Programme selection, application
│
├── public_api/            # Public API blueprint
│   └── routes.py         # Public endpoints (programmes list)
│
├── database/              # Database files
│   ├── schema.sql        # Complete database schema
│   ├── seed_data.sql     # Sample data for testing
│   └── migrations/       # Database migration scripts
│
└── frontend/              # Static HTML/CSS/JS files
    ├── index.html        # Landing page
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── student/          # Student portal pages
    ├── admin/            # Admin portal pages
    └── assets/           # CSS, JS, images
        ├── css/
        │   └── style.css # Main stylesheet
        └── js/
            ├── api.js    # API helper functions
            └── layout.js # Sidebar/header components
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - New student registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current session

### Student
- `GET /student/dashboard` - Dashboard data
- `GET /student/profile` - Profile information
- `PUT /student/profile` - Update profile
- `GET /student/results` - Academic results
- `GET /student/timetable` - Personal timetable

### Registration
- `GET /registration/courses` - Browse available courses
- `GET /registration/units` - Browse available units (alias)
- `POST /registration/register` - Register for courses
- `GET /registration/my-courses` - View registered courses
- `GET /registration/my-units` - View registered units (alias)
- `GET /registration/history` - Registration history

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/students` - Student list
- `POST /admin/students` - Add new student
- `GET /admin/registrations` - Registration requests
- `PUT /admin/registrations/:id/approve` - Approve registration

## Features & Technologies

### Backend
- **Flask** - Python web framework
- **MySQL** - Database
- **Blueprints** - Modular application structure
- **Session-based authentication** - Secure user sessions
- **bcrypt** - Password hashing
- **CORS** - Cross-origin resource sharing

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Bootstrap Icons** - Icon library
- **Responsive Design** - Mobile-friendly
- **Modern UI** - Pink theme with dark sidebar
- **Toast Notifications** - User feedback
- **Client-side routing** - SPA-like navigation

### Security
- ✅ Password hashing with bcrypt
- ✅ Session management
- ✅ SQL injection prevention (parameterized queries)
- ✅ CSRF protection
- ✅ Role-based access control
- ✅ Input validation

## Common Issues & Solutions

### Issue: "Failed to load courses"
**Cause:** No active units in database or missing programme assignment

**Solution:**
```bash
python verify_database.py
# Check if active units exist
# Run seed_data.sql if needed
```

### Issue: Cannot connect to database
**Cause:** MySQL not running or wrong credentials

**Solution:**
1. Start MySQL server
2. Check credentials in `config.py`
3. Verify database exists: `SHOW DATABASES;`

### Issue: 404 errors on API calls
**Cause:** Flask server not running or wrong URL

**Solution:**
1. Make sure Flask is running: `python app.py`
2. Check browser console for actual error
3. Verify endpoint exists in routes

### Issue: Login fails with correct credentials
**Cause:** Password hash mismatch or logging error

**Solution:**
```sql
-- Reset a user's password
UPDATE users 
SET password_hash = '$2b$12$...' 
WHERE email = 'user@example.com';

-- Or use bcrypt to generate new hash
```

## Development

### Adding New Features

1. **New Route:**
   - Add endpoint in appropriate blueprint (`student/`, `admin/`, etc.)
   - Use `@login_required` decorator for protected routes
   - Return JSON responses

2. **New Page:**
   - Create HTML in `frontend/student/` or `frontend/admin/`
   - Use existing `api.js` for API calls
   - Follow existing UI patterns

3. **Database Changes:**
   - Create migration file in `database/migrations/`
   - Test thoroughly before applying to production

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

## Testing

Run individual test scripts:
```bash
python test_database_connectivity.py
python test_endpoints_quick.py
python verify_database.py
```

## Deployment

### Production Checklist
- [ ] Change `SECRET_KEY` in config
- [ ] Set `DEBUG = False`
- [ ] Use production database
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure firewall
- [ ] Set up backups
- [ ] Use environment variables for secrets

### Recommended Stack
- **Web Server:** Nginx
- **WSGI Server:** Gunicorn
- **Database:** MySQL 8.0+
- **OS:** Ubuntu Server 20.04+

## Support

For issues or questions:
1. Check this README
2. Review test documentation in `TEST_SYSTEM.md`
3. Check system fixes in `SYSTEM_FIXES_SUMMARY.md`
4. Examine Flask console output for errors

## License

This project is for educational purposes.

## Credits

Developed as a Software Engineering project.
