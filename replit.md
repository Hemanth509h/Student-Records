# Student Management System - Project Documentation

## Project Overview
This is a comprehensive Flask-based student management system that allows administrators, teachers, and staff to manage student records, grades, and generate reports. The system includes user authentication, student CRUD operations, custom SQL queries, and statistical reporting.

## Project Structure

### Core Python Files

1. **main.py**
   - Entry point for the Flask application
   - Runs the development server on port 5000
   - Configured to bind to 0.0.0.0 for Replit compatibility

2. **core/models.py**
   - Defines database models using SQLAlchemy ORM
   - **User Model**: Handles user authentication with roles (admin, teacher, student, parent, staff)
   - **Student Model**: Stores student information including roll number, name, email, courses, and grades
   - Includes helper methods like `to_dict()` and `get_average_grade()`

3. **core/app.py**
   - Main Flask application configuration
   - Defines all application routes and their handlers
   - **Routes**:
     - `/login` - User authentication
     - `/logout` - User logout
     - `/` - Main dashboard showing all students and statistics
     - `/add_student` - Form to add new students
     - `/edit_student/<roll_no>` - Edit existing student
     - `/delete_student/<roll_no>` - Delete student record
     - `/query` - Custom SQL query interface (SELECT only for security)
     - `/reports` - Statistical reports with grade distribution and performance analysis
     - `/search` - Search students by name, roll number, or email
     - `/export` - Export all student data as JSON

4. **add_5000_students.py**
   - Utility script to populate database with sample data
   - Creates 5 sample user accounts (admin, teachers, staff, parent)
   - Generates 5000 random student records with realistic data
   - Uses batch processing for efficient database insertion

### Template Files (HTML)

All templates are located in the `templates/` directory:

1. **base.html** - Base template with navigation and layout
   - Contains all CSS styling in `<style>` tags
   - Defines navigation bar with search functionality
   - Provides flash message display system
   - Includes footer
   - Uses Jinja2 template blocks for content extension

2. **login.html** - User login page (FULLY COMMENTED)
   - Simple login form with email and password
   - Floating label effect for better UX
   - Extends base.html template
   - Form submits to /login route via POST

3. **index.html** - Main dashboard showing student list and statistics
   - Statistics cards (total students, courses, average grade)
   - Quick action buttons (Add, Query, Reports, Export)
   - Student data table with inline edit/delete actions
   - Search results display
   - Color-coded grade badges
   - Auto-refresh functionality (every 30 seconds)

4. **add_student.html** - Form to add new student
   - Input fields for roll number, name, email
   - Courses input (comma-separated)
   - Grades input (comma-separated, must match courses)
   - Real-time validation to ensure course count matches grade count
   - Help card with instructions
   - Client-side form validation

5. **edit_student.html** - Form to edit existing student
   - Similar to add_student but pre-populated with existing data
   - Roll number field is readonly (cannot be changed)
   - Uses Jinja2 filters to join arrays for display
   - Same validation as add form

6. **query.html** - Custom SQL query interface
   - Textarea for SQL query input
   - Example queries section (toggleable)
   - Results display table
   - Quick reference guide for available fields
   - Syntax highlighting on blur
   - Helper functions in JavaScript

7. **reports.html** - Statistical reports and analytics
   - Overview statistics cards
   - Grade distribution chart
   - Per-course statistics
   - Top 5 performers table
   - Low performers (below 70) table
   - Export functionality
   - Custom CSS for charts and layouts

8. **coming_soon.html** - Placeholder page for future features
   - Simple centered layout
   - Purple gradient background
   - Standalone page (doesn't extend base.html)

### Database Structure

The application uses SQLite database (students.db) with two main tables:

#### Users Table
- `id` - Primary key
- `email` - Unique login email (indexed)
- `username` - Display name
- `password_hash` - Hashed password (never stores plain text)
- `role` - User role (admin/teacher/student/parent/staff)
- `first_name`, `last_name` - User's name
- `phone` - Contact number
- `active` - Account status
- `last_login` - Last login timestamp
- `profile_picture` - Profile picture URL
- `created_at`, `updated_at` - Timestamps

#### Students Table
- `id` - Primary key
- `roll_no` - Unique student ID (e.g., STU00001)
- `name` - Student's full name
- `email` - Student's email
- `courses` - JSON array of enrolled courses
- `grades` - JSON array of corresponding grades
- `created_at` - Record creation timestamp

## Key Features

### 1. User Authentication
- Secure login with password hashing
- Role-based access control
- Session management with Flask-Login
- All pages except login require authentication

### 2. Student Management
- **Add Students**: Create new student records with courses and grades
- **Edit Students**: Update student information
- **Delete Students**: Remove student records
- **Search**: Find students by name, roll number, or email

### 3. Reports and Analytics
- Overall statistics (total students, courses, average grade)
- Grade distribution (A, B, C, D, F)
- Per-course statistics and averages
- Top 5 performers
- Bottom 10 low performers (below 70)
- Visual summary of student performance

### 4. Custom Query Interface
- Secure SQL query execution (SELECT only)
- Built-in security checks to prevent data modification
- Query length limit (1000 characters)
- Result pagination (max 100 rows displayed)

### 5. Data Export
- Export all student data as JSON
- Downloadable file format
- Includes all student information

## Sample Login Credentials

After running `python add_5000_students.py`, use these credentials:

- **Admin**: admin@school.com / admin123
- **Teacher**: teacher1@school.com / teacher123
- **Staff**: staff@school.com / staff123
- **Parent**: parent1@example.com / parent123

## Running the Application

### Development Mode
```bash
python main.py
```
Server runs on http://0.0.0.0:5000

### Populate Sample Data
```bash
python add_5000_students.py
```
This creates 5 users and 5000 student records.

## Technology Stack

- **Backend**: Flask 3.1.2
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Forms**: Flask-WTF for CSRF protection
- **Email Validation**: email-validator library
- **Production Server**: Gunicorn (for deployment)

## Security Features

1. **Password Security**: All passwords are hashed using Werkzeug's `generate_password_hash`
2. **CSRF Protection**: Flask-WTF provides CSRF tokens
3. **SQL Injection Prevention**: 
   - Query interface blocks all mutating SQL commands
   - SQLAlchemy ORM prevents injection in regular operations
4. **Session Security**: Secret key used for session encryption
5. **Login Required**: All routes except login require authentication

## Code Organization

### Separation of Concerns
- **Models** (core/models.py): Database schema and data validation
- **Views** (core/app.py): Request handling and business logic
- **Templates**: HTML presentation layer
- **Utilities**: Helper scripts like add_5000_students.py

### Data Validation
- Email format validation
- Grade number validation
- Course-grade count matching
- Duplicate roll number prevention

## Performance Considerations

1. **Batch Processing**: Student insertion uses `bulk_save_objects()` for efficiency
2. **Indexed Fields**: Email field is indexed for fast login lookups
3. **Query Pagination**: Results limited to 100 rows to prevent overwhelming the UI
4. **Database Optimization**: `SQLALCHEMY_TRACK_MODIFICATIONS` disabled to save memory

## Development Notes

### Adding New Features
1. Define route in `core/app.py`
2. Create corresponding template in `templates/`
3. Update navigation in `base.html` if needed
4. Add appropriate authentication decorators

### Database Changes
1. Modify models in `core/models.py`
2. Consider using migrations for production (e.g., Flask-Migrate)
3. Update `add_5000_students.py` if schema changes affect sample data

## Common Operations

### Reset Database
Delete `instance/students.db` and restart the application. Tables will be recreated automatically.

### Add Sample Data
Run `python add_5000_students.py` - it checks for existing records and won't create duplicates.

### View SQL Queries
All database operations use SQLAlchemy ORM, which can be debugged by enabling SQL logging in Flask config.

## Project Status

This is a fully functional student management system with:
- ✅ User authentication
- ✅ Student CRUD operations  
- ✅ Search functionality
- ✅ Reports and analytics
- ✅ Custom query interface
- ✅ Data export
- ✅ Comprehensive code comments
- ✅ Security features

## Future Enhancements (Potential)
- Attendance tracking
- Grade history/changelog
- Email notifications
- Advanced reporting with charts
- Course management
- Student-parent relationships
- Academic year/semester management
- File uploads (transcripts, documents)
