# Student Record Management System

## Overview

This is a Flask-based web application for managing student records with a SQLite database backend. The system provides a platform for storing, retrieving, querying, and analyzing student data with a clean, modern interface.

## Recent Changes (November 6, 2025)

- **Database Migration**: Successfully migrated from PostgreSQL to SQLite for simplified deployment
- **Models Updated**: Converted PostgreSQL ARRAY types to JSON for SQLite compatibility
- **Dependencies Cleaned**: Removed psycopg2-binary and PostgreSQL-specific dependencies
- **Database File**: Using `students.db` as the local SQLite database
- **Migration Completed**: Successfully migrated from Replit Agent to standard Replit environment
- **Sample Data**: Populated with 5000+ student records and multiple user accounts

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Web Framework**: Flask serves as the main application layer providing routes, template rendering, and request handling
- **Database**: SQLite database with SQLAlchemy ORM for data persistence
- **Authentication**: Flask-Login for user session management with role-based access control
- **Models**: User model for authentication and Student model for student records with courses and grades

### Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template providing consistent dark theme layout
- **Styling Framework**: Bootstrap 5 with custom CSS implementing a modern dark theme design
- **Client-Side Scripting**: Vanilla JavaScript for form validation, interactive features, and search functionality
- **Responsive Design**: Mobile-first approach ensuring functionality across different screen sizes

### Database Schema
- **users**: User accounts with email, password hash, role, and profile information
- **students**: Student records with roll number, name, email, courses (JSON), and grades (JSON)

### Security and Session Management
- **Session Handling**: Flask sessions with environment-configurable secret keys (SESSION_SECRET)
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Input Validation**: Comprehensive form validation on both client and server sides
- **Query Protection**: SQL injection prevention with parameterized queries and read-only query interface

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: Comprehensive UI framework providing responsive grid system, components, and utilities
- **Font Awesome 6.4.0**: Icon library providing consistent visual elements

### Python Dependencies
- **Flask**: Core web framework handling routing, templating, and request processing
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session and authentication management
- **Flask-WTF**: Form handling and validation
- **Gunicorn**: Production-ready WSGI HTTP server
- **email-validator**: Email validation utilities
- **SQLAlchemy**: Database toolkit and ORM
- **Werkzeug**: WSGI utilities and security features

### Development Environment
- **Replit Platform**: Configured for cloud-based development with proper host binding (0.0.0.0:5000)
- **Environment Variables**: SESSION_SECRET for secure session management
- **Deployment**: Configured for autoscale deployment with Gunicorn
- **Database**: SQLite file-based database (`students.db`)

## Application Features

### Core Functionality
1. **Student Management**: Add, edit, delete, and view student records
2. **Course Tracking**: Each student can have multiple courses with corresponding grades
3. **Search**: Search students by name, roll number, or email
4. **Reports**: Generate statistics including top performers, grade distribution, and course analytics
5. **Custom Queries**: Execute read-only SQL queries for advanced data analysis
6. **Data Export**: Export student data as JSON

### Access Control
- Admin login (default: admin@school.com / admin123)
- Protected routes requiring authentication
- Role-based user system (admin, teacher, student, parent, staff)

### Sample Data
- 5000+ student records with realistic data
- Multiple user accounts with different roles
- Diverse course and grade combinations

## Project Structure
```
/
├── core/
│   ├── app.py          # Main Flask application with routes
│   └── models.py       # Database models (User, Student)
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Base template with navigation
│   ├── login.html      # Login page
│   ├── index.html      # Dashboard with student list
│   ├── add_student.html
│   ├── edit_student.html
│   ├── query.html      # Custom SQL query interface
│   └── reports.html    # Analytics and reports
├── main.py             # Application entry point
├── add_5000_students.py  # Data population script
├── requirements.txt    # Python dependencies
└── students.db         # SQLite database file
```

## Default Login Credentials

**Admin Account:**
- Email: admin@school.com
- Password: admin123

## Database Information

- **Type**: SQLite (file-based)
- **Location**: `students.db` in project root
- **Tables**: users, students
- **Data Format**: JSON for arrays (courses and grades)

## Development

### Running the Application
The application is configured to run automatically with Gunicorn on port 5000:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Populating Sample Data
Run the data population script to add 5000+ students:
```bash
python add_5000_students.py
```

### Key Features for Developers
- Automatic database initialization on startup
- Hot reload enabled in development
- Debug logging configured
- Session management with secure cookies
- CSRF protection with Flask-WTF

## Deployment

- **Target**: Replit Autoscale
- **Server**: Gunicorn WSGI server
- **Port**: 5000
- **Database**: SQLite (persisted in deployment)
- **Environment**: Python 3.11

## Security Notes

- Never commit the database file with real user data
- Change default admin credentials in production
- Set SESSION_SECRET environment variable
- All passwords are hashed with Werkzeug
- SQL queries are parameterized to prevent injection
- Input validation on both client and server sides
