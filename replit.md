# Student Record Management System

## Overview

This is a Flask-based web application for managing student records with a PostgreSQL database backend. The system provides a platform for storing, retrieving, querying, and analyzing student data with a clean, modern interface.

## Recent Changes (October 15, 2025)

- **Database Schema Cleanup**: Simplified from 35+ tables to only 2 essential tables (users and students)
- **Models Simplified**: Removed all unused models, keeping only User and Student
- **create_tables.py Updated**: Simplified initialization script for the streamlined schema
- **Migration Completed**: Successfully migrated from Replit Agent to standard Replit environment

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Web Framework**: Flask serves as the main application layer providing routes, template rendering, and request handling
- **Database**: PostgreSQL database with SQLAlchemy ORM for data persistence
- **Authentication**: Flask-Login for user session management with role-based access control
- **Models**: User model for authentication and Student model for student records with courses and grades

### Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template providing consistent dark theme layout
- **Styling Framework**: Bootstrap 5 with custom CSS implementing a modern dark theme design
- **Client-Side Scripting**: Vanilla JavaScript for form validation, interactive features, and search functionality
- **Responsive Design**: Mobile-first approach ensuring functionality across different screen sizes

### Database Schema
- **users**: User accounts with email, password hash, role, and profile information
- **students**: Student records with roll number, name, email, courses (array), and grades (array)

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
- **psycopg2-binary**: PostgreSQL database adapter
- **Gunicorn**: Production-ready WSGI HTTP server
- **email-validator**: Email validation utilities

### Development Environment
- **Replit Platform**: Configured for cloud-based development with proper host binding (0.0.0.0:5000)
- **Environment Variables**: DATABASE_URL and SESSION_SECRET for configuration management
- **Deployment**: Configured for autoscale deployment with Gunicorn

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
├── create_tables.py    # Database initialization script
└── requirements.txt    # Python dependencies
```
