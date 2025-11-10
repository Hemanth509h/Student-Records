# Import os module for accessing environment variables
import os
# Import secrets module for generating secure random keys
import secrets
# Import Flask components for web application functionality
from flask import Flask, render_template, request, redirect, url_for, flash, Response, session
# Import SQLAlchemy for database ORM (Object Relational Mapping)
from flask_sqlalchemy import SQLAlchemy
# Import Flask-Login components for user authentication and session management
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# Import Werkzeug security functions for password hashing and verification
from werkzeug.security import generate_password_hash, check_password_hash
# Import email validation library to validate email format
from email_validator import validate_email, EmailNotValidError
# Import database instance and model classes from our models module
from core.models import db, Student, User
# Import SQLAlchemy text and or_ for raw SQL queries and OR conditions
from sqlalchemy import text, or_
# Import json module for handling JSON data export
import json

# Create Flask application instance
# __name__ helps Flask find resources like templates
# template_folder specifies where HTML templates are located
# static_folder specifies where static files (CSS, JS, images) are located
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configure secret key for session encryption and CSRF protection
# First, try to get secret key from environment variable (secure for production)
app.secret_key = os.environ.get("SESSION_SECRET")
# If environment variable is not set (development environment)
if not app.secret_key:
    # Generate a random 32-byte hexadecimal secret key for development
    app.secret_key = secrets.token_hex(32)
    # Print warning to console that this is not secure for production
    print("WARNING: Using generated random secret key for development. Set SESSION_SECRET environment variable in production.")

# Configure database connection using SQLite
# SQLite stores the database in a single file (students.db) in the instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# Disable modification tracking to save memory and improve performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with our Flask app
# This connects the db instance from models.py to this Flask application
db.init_app(app)

# Initialize Flask-Login extension for handling user authentication
login_manager = LoginManager()
# Connect the login manager to our Flask app
login_manager.init_app(app)
# Specify which route/function handles user login
login_manager.login_view = 'login'
# Message to display when user tries to access protected page without login
login_manager.login_message = 'Please log in to access this page.'
# Category of flash message (info, warning, error, success)
login_manager.login_message_category = 'info'


# Database initialization function
# This function creates all database tables defined in our models
def init_db():
    """Initialize database tables"""
    # Create an application context to access database
    with app.app_context():
        # Create all tables defined in models.py (User, Student, etc.)
        db.create_all()

# Initialize database on application startup
# Try to create tables when the application starts
try:
    # Call the initialization function
    init_db()
# If database initialization fails (e.g., permissions, already exists)
except Exception as e:
    # Print warning message with error details
    print(f"Warning: Could not initialize database: {e}")
    # Inform that database will be created on first use instead
    print("Database will be created on first use")

# User loader callback for Flask-Login
# This function is called to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID"""
    # Query the User table to find user by ID and return the User object
    # Convert user_id to integer as it's stored as string in session
    return User.query.get(int(user_id))

# --- Login route ---
# Define route for login page that accepts both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    # Check if this is a POST request (user submitted the login form)
    if request.method == 'POST':
        # Get email from form data, remove whitespace, and convert to lowercase
        email = request.form['email'].strip().lower()
        # Get password from form data (don't modify password)
        password = request.form['password']

        # Validate that both email and password are provided
        if not email or not password:
            # Show error message if either field is empty
            flash('Email and password are required', 'error')
            # Return to login page with error message
            return render_template('login.html')
        
        # Query database to find user with matching email
        user = User.query.filter_by(email=email).first()
        # Check if user exists and password hash matches the provided password
        if user and check_password_hash(user.password_hash, password):
            # Log the user in by creating a session
            login_user(user)
            # Show success message
            flash('Login successful!', 'success')
            # Redirect to main dashboard
            return redirect(url_for('index'))

        # If email or password is incorrect, show error message
        flash('Invalid email or password', 'error')

    # For GET requests, just show the login page
    return render_template('login.html')

# Define route for logging out
# Decorator requires user to be logged in to access this route
@app.route('/logout')
@login_required
def logout():
    """User logout"""
    # Clear the user's session and log them out
    logout_user()
    # Show informational message
    flash('You have been logged out', 'info')
    # Redirect user back to login page
    return redirect(url_for('login'))

# Define route for home/dashboard page (main page of application)
# Decorator requires user to be logged in to access this route
@app.route('/')
@login_required
def index():
    """Main dashboard showing all students"""
    # Query all students from database, ordered alphabetically by name
    students = Student.query.order_by(Student.name).all()
    # Convert student objects to dictionaries for easier template rendering
    students_data = [student.to_dict() for student in students]
    
    # Calculate statistics to display on dashboard
    # Count total number of students
    total_students = len(students_data)
    # Create empty lists to collect all courses and grades
    all_courses = []
    all_grades = []
    # Loop through each student to gather their courses and grades
    for student in students_data:
        # Add all of this student's courses to the list
        all_courses.extend(student['courses'])
        # Add all of this student's grades to the list
        all_grades.extend(student['grades'])
    
    # Count unique courses (using set to remove duplicates)
    total_courses = len(set(all_courses))
    # Calculate average grade across all students
    # Use conditional to avoid division by zero if no grades exist
    avg_grade = sum(all_grades) / len(all_grades) if all_grades else 0
    
    # Create a dictionary with all statistics
    stats = {
        'total_students': total_students,  # Total number of students
        'total_courses': total_courses,  # Total number of unique courses
        'avg_grade': round(avg_grade, 2)  # Average grade rounded to 2 decimals
    }
    
    # Render the index template with students data and statistics
    return render_template('index.html', students=students_data, stats=stats)

# Define route for adding a new student (accepts GET and POST)
# Decorator requires user to be logged in to access this route
@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student"""
    # Check if form was submitted (POST request)
    if request.method == 'POST':
        # Get form data and remove extra whitespace
        roll_no = request.form['roll_no'].strip()  # Student's roll/ID number
        name = request.form['name'].strip()  # Student's name
        email = request.form['email'].strip()  # Student's email
        courses_str = request.form['courses'].strip()  # Comma-separated course names
        grades_str = request.form['grades'].strip()  # Comma-separated grades
        
        # Validate that all required fields are provided
        # all() returns True only if all items in the list are truthy (non-empty)
        if not all([roll_no, name, email, courses_str, grades_str]):
            # Show error message if any field is missing
            flash('All fields are required', 'error')
            # Return to add student page with error
            return render_template('add_student.html')
        
        # Parse comma-separated courses into a list
        # Split by comma and strip whitespace from each course name
        courses = [course.strip() for course in courses_str.split(',')]
        # Try to parse grades into list of floats
        try:
            # Split by comma, strip whitespace, and convert each to float
            grades = [float(grade.strip()) for grade in grades_str.split(',')]
        # If conversion fails (non-numeric grade entered)
        except ValueError:
            # Show error message for invalid grade format
            flash('Grades must be valid numbers', 'error')
            # Return to add student page with error
            return render_template('add_student.html')
        
        # Validate that number of courses matches number of grades
        if len(courses) != len(grades):
            # Show error if mismatch (each course needs a grade)
            flash('Number of courses must match number of grades', 'error')
            # Return to add student page with error
            return render_template('add_student.html')
        
        # Check if a student with this roll number already exists
        existing_student = Student.query.filter_by(roll_no=roll_no).first()
        # If roll number is already in use
        if existing_student:
            # Show error message (roll numbers must be unique)
            flash('Roll number already exists', 'error')
            # Return to add student page with error
            return render_template('add_student.html')
        
        # Try to add the student to the database
        try:
            # Create a new Student object
            student = Student()
            # Set student's roll number
            student.roll_no = roll_no
            # Set student's name
            student.name = name
            # Set student's email
            student.email = email
            # Set student's courses list
            student.courses = courses
            # Set student's grades list
            student.grades = grades
            # Add student to the database session
            db.session.add(student)
            # Commit the transaction to save to database
            db.session.commit()
            # Show success message
            flash('Student added successfully!', 'success')
            # Redirect to main page to see the new student
            return redirect(url_for('index'))
        # If database operation fails
        except Exception as e:
            # Rollback the transaction to undo any partial changes
            db.session.rollback()
            # Show generic error message
            flash('Error adding student. Please try again.', 'error')
            # Return to add student page
            return render_template('add_student.html')
    
    # For GET requests, just show the add student form
    return render_template('add_student.html')

# Define route for editing a student (roll_no is passed as URL parameter)
# Decorator requires user to be logged in to access this route
@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
@login_required
def edit_student(roll_no):
    """Edit an existing student"""
    # Find the student in database by roll number
    student = Student.query.filter_by(roll_no=roll_no).first()
    # Check if student exists
    if not student:
        # Show error if student not found
        flash('Student not found', 'error')
        # Redirect back to main page
        return redirect(url_for('index'))
    
    # Check if form was submitted (POST request)
    if request.method == 'POST':
        # Get updated form data and remove extra whitespace
        name = request.form['name'].strip()  # Updated name
        email = request.form['email'].strip()  # Updated email
        courses_str = request.form['courses'].strip()  # Updated courses
        grades_str = request.form['grades'].strip()  # Updated grades
        
        # Validate that all required fields are provided
        if not all([name, email, courses_str, grades_str]):
            # Show error if any field is missing
            flash('All fields are required', 'error')
            # Return to edit page with current student data
            return render_template('edit_student.html', student=student.to_dict())
        
        # Parse comma-separated courses into a list
        courses = [course.strip() for course in courses_str.split(',')]
        # Try to parse grades into list of floats
        try:
            # Split by comma and convert each to float
            grades = [float(grade.strip()) for grade in grades_str.split(',')]
        # If conversion fails (invalid grade format)
        except ValueError:
            # Show error message
            flash('Grades must be valid numbers', 'error')
            # Return to edit page with current student data
            return render_template('edit_student.html', student=student.to_dict())
        
        # Validate that courses and grades have same length
        if len(courses) != len(grades):
            # Show error if mismatch
            flash('Number of courses must match number of grades', 'error')
            # Return to edit page with current student data
            return render_template('edit_student.html', student=student.to_dict())
        
        # Try to update the student in database
        try:
            # Update student's name
            student.name = name
            # Update student's email
            student.email = email
            # Update student's courses
            student.courses = courses
            # Update student's grades
            student.grades = grades
            # Commit changes to database
            db.session.commit()
            # Show success message
            flash('Student updated successfully!', 'success')
            # Redirect to main page
            return redirect(url_for('index'))
        # If database update fails
        except Exception as e:
            # Rollback the transaction
            db.session.rollback()
            # Show error message
            flash('Error updating student. Please try again.', 'error')
    
    # For GET requests, show edit form with current student data
    return render_template('edit_student.html', student=student.to_dict())

# Define route for deleting a student (only accepts POST for security)
# Decorator requires user to be logged in to access this route
@app.route('/delete_student/<roll_no>', methods=['POST'])
@login_required
def delete_student(roll_no):
    """Delete a student"""
    # Find student in database by roll number
    student = Student.query.filter_by(roll_no=roll_no).first()
    # Check if student exists
    if student:
        # Try to delete the student
        try:
            # Mark student for deletion in the session
            db.session.delete(student)
            # Commit the transaction to permanently delete
            db.session.commit()
            # Show success message
            flash('Student deleted successfully!', 'success')
        # If deletion fails
        except Exception as e:
            # Rollback the transaction
            db.session.rollback()
            # Show error message
            flash('Error deleting student', 'error')
    # If student doesn't exist
    else:
        # Show error message
        flash('Student not found', 'error')
    
    # Redirect back to main page
    return redirect(url_for('index'))

# Define route for custom SQL query interface
# Decorator requires user to be logged in to access this route
@app.route('/query', methods=['GET', 'POST'])
@login_required
def query():
    """Custom query interface"""
    # Initialize results as None (no query executed yet)
    results = None
    
    # Check if form was submitted (POST request)
    if request.method == 'POST':
        # Get the SQL query text from form and remove whitespace
        query_text = request.form['query'].strip()
        # Check if query text is not empty
        if query_text:
            # Try to execute the query with security checks
            try:
                # List of dangerous SQL keywords that could modify data
                forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
                # Check if query contains any forbidden keywords (case-insensitive)
                if any(keyword in query_text.upper() for keyword in forbidden_keywords):
                    # Show error if query tries to modify data
                    flash('Only SELECT queries are allowed', 'error')
                # Check if query is too long (prevent denial of service)
                elif len(query_text) > 1000:
                    # Show error if query exceeds character limit
                    flash('Query too long (max 1000 characters)', 'error')
                # Check if query starts with SELECT (safe read-only operation)
                elif query_text.upper().startswith('SELECT'):
                    # Execute the raw SQL query using SQLAlchemy's text function
                    result = db.session.execute(text(query_text))
                    # Convert result rows to list of lists for template rendering
                    results = [list(row) for row in result.fetchall()]
                    # Check if results exceed display limit
                    if len(results) > 100:
                        # Limit to first 100 results to prevent overwhelming the page
                        results = results[:100]
                        # Show success message indicating results are truncated
                        flash(f'Query executed successfully. Showing first 100 results.', 'success')
                    # If results fit within limit
                    else:
                        # Show success message with total count
                        flash(f'Query executed successfully. Found {len(results)} results.', 'success')
                # If query doesn't start with SELECT
                else:
                    # Show error message (only SELECT allowed)
                    flash('Only SELECT queries are allowed', 'error')
            # If query execution fails (syntax error, invalid table, etc.)
            except Exception as e:
                # Show error message with details
                flash(f'Query error: {str(e)}', 'error')
    
    # Render query page with results (empty list if no results)
    return render_template('query.html', results=results or [])


# Define route for generating statistical reports
# Decorator requires user to be logged in to access this route
@app.route('/reports')
@login_required
def reports():
    """Generate reports"""
    # Try to generate reports (wrap in try/except for error handling)
    try:
        # Query all students from database
        students = Student.query.all()
        # Convert student objects to dictionaries
        students_data = [student.to_dict() for student in students]
        
        # Count total number of students
        total_students = len(students_data)
        
        # Check if there are any students in the database
        if total_students == 0:
            # Show warning if no students found
            flash('No students found to generate reports', 'warning')
            # Return empty report page
            return render_template('reports.html', report_data={})
        
        # Initialize dictionaries for course statistics and grade distribution
        # course_stats will track students and grades per course
        course_stats = {}
        # grade_distribution counts how many A's, B's, C's, D's, F's
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        # Loop through each student to calculate statistics
        for student_data in students_data:
            # Get list of courses for this student
            courses = student_data['courses']
            # Get list of grades for this student
            grades = student_data['grades']
            
            # Zip courses and grades together to process each pair
            for course, grade in zip(courses, grades):
                # Check if we've seen this course before
                if course not in course_stats:
                    # Initialize statistics for this course
                    course_stats[course] = {'total_students': 0, 'total_grade': 0, 'avg_grade': 0}
                
                # Increment student count for this course
                course_stats[course]['total_students'] += 1
                # Add this grade to the total for averaging
                course_stats[course]['total_grade'] += grade
                
                # Categorize grade into letter grade distribution
                # 90+ is A
                if grade >= 90:
                    grade_distribution['A'] += 1
                # 80-89 is B
                elif grade >= 80:
                    grade_distribution['B'] += 1
                # 70-79 is C
                elif grade >= 70:
                    grade_distribution['C'] += 1
                # 60-69 is D
                elif grade >= 60:
                    grade_distribution['D'] += 1
                # Below 60 is F
                else:
                    grade_distribution['F'] += 1
        
        # Calculate average grades for each course
        # Loop through all courses we found
        for course in course_stats:
            # Check if course has students (avoid division by zero)
            if course_stats[course]['total_students'] > 0:
                # Calculate average: total grades / number of students
                # Round to 2 decimal places
                course_stats[course]['avg_grade'] = round(
                    course_stats[course]['total_grade'] / course_stats[course]['total_students'], 2
                )
        
        # Find top performing students
        # Create empty list to store top performers
        top_performers = []
        # Loop through all students
        for student in students:
            # Calculate this student's average grade
            avg_grade = student.get_average_grade()
            # Add student info to list
            top_performers.append({
                'name': student.name,  # Student's name
                'roll_no': student.roll_no,  # Student's roll number
                'avg_grade': avg_grade,  # Student's average grade
                'courses': student.courses  # List of student's courses
            })
        
        # Sort students by average grade in descending order (highest first)
        top_performers.sort(key=lambda x: x['avg_grade'], reverse=True)
        # Keep only top 5 students
        top_performers = top_performers[:5]
        
        # Find low performing students who may need attention
        # Students with average below 70 are considered low performers
        low_performers = []
        # Loop through all students
        for student in students:
            # Calculate this student's average grade
            avg_grade = student.get_average_grade()
            # Check if average is below 70 (threshold for concern)
            if avg_grade < 70:
                # Add student info to low performers list
                low_performers.append({
                    'name': student.name,  # Student's name
                    'roll_no': student.roll_no,  # Student's roll number
                    'avg_grade': avg_grade,  # Student's average grade
                    'courses': student.courses  # List of student's courses
                })
        
        # Sort low performers by grade (lowest first)
        low_performers.sort(key=lambda x: x['avg_grade'])
        # Keep only bottom 10 students
        low_performers = low_performers[:10]
        
        # Calculate overall average across all students and courses
        # Create empty list to collect all grades
        all_grades = []
        # Loop through all students
        for student_data in students_data:
            # Add all of this student's grades to the list
            all_grades.extend(student_data['grades'])
        # Calculate overall average (sum all grades / count)
        # Use conditional to avoid division by zero
        overall_avg = round(sum(all_grades) / len(all_grades), 2) if all_grades else 0
        
        # Package all report data into a dictionary
        report_data = {
            'total_students': total_students,  # Total number of students
            'total_courses': len(course_stats),  # Total number of unique courses
            'overall_avg': overall_avg,  # Overall average grade
            'course_stats': course_stats,  # Per-course statistics
            'grade_distribution': grade_distribution,  # Distribution of letter grades
            'top_performers': top_performers,  # Top 5 students
            'low_performers': low_performers  # Bottom 10 students (below 70)
        }
        
        # Render the reports template with all the data
        return render_template('reports.html', report_data=report_data)
        
    # If any error occurs during report generation
    except Exception as e:
        # Show error message to user
        flash('An error occurred while generating reports', 'error')
        # Redirect back to main page
        return redirect(url_for('index'))

# Define route for searching students
# Decorator requires user to be logged in to access this route
@app.route('/search')
@login_required
def search():
    """Search students"""
    # Get search term from URL query parameters (GET request)
    # Default to empty string if not provided, then strip whitespace
    search_term = request.args.get('search', '').strip()
    # Initialize empty list for results
    students_data = []
    
    # Only search if a search term was provided
    if search_term:
        # Use SQLAlchemy ORM to search for students
        # ilike() performs case-insensitive search (LIKE in SQL)
        # % wildcards match any characters before/after search term
        # or_() allows matching any of the fields (name OR roll_no OR email)
        students = Student.query.filter(
            or_(
                Student.name.ilike(f'%{search_term}%'),  # Search in name
                Student.roll_no.ilike(f'%{search_term}%'),  # Search in roll number
                Student.email.ilike(f'%{search_term}%')  # Search in email
            )
        ).all()  # Execute query and get all matching results
        
        # Convert student objects to dictionaries for template
        students_data = [student.to_dict() for student in students]
    
    # Render index template with search results
    # Pass search term to show what was searched
    # Pass minimal stats (only total students count, rest set to 0)
    return render_template('index.html', students=students_data, search_term=search_term, stats={'total_students': len(students_data), 'total_courses': 0, 'avg_grade': 0})

# Define route for exporting student data to JSON file
# Decorator requires user to be logged in to access this route
@app.route('/export')
@login_required
def export():
    """Export students data as JSON"""
    # Query all students from database
    students = Student.query.all()
    # Convert all student objects to dictionaries
    students_data = [student.to_dict() for student in students]
    
    # Create JSON string from student data
    # indent=2 makes the JSON readable with 2-space indentation
    # default=str converts non-JSON types (like datetime) to strings
    json_data = json.dumps(students_data, indent=2, default=str)
    
    # Return JSON data as downloadable file
    return Response(
        json_data,  # The JSON content to send
        mimetype='application/json',  # Tell browser this is JSON
        headers={'Content-Disposition': 'attachment; filename=students_export.json'}  # Force download with filename
    )


# Check if this script is being run directly (not imported)
if __name__ == '__main__':
    # Run Flask development server
    # debug=True enables debug mode with auto-reload
    # host='0.0.0.0' makes server accessible from any network interface
    # port=5000 specifies the port to listen on
    app.run(debug=True, host='0.0.0.0', port=5000)