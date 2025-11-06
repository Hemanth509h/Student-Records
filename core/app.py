import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, Response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from core.models import db, Student, User
from sqlalchemy import text, or_
import json

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Set secret key from environment or generate random for development
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    # Generate a random secret for development only
    app.secret_key = secrets.token_hex(32)
    print("WARNING: Using generated random secret key for development. Set SESSION_SECRET environment variable in production.")

# Database configuration - SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# Database initialization function
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")
    print("Database will be created on first use")

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID"""
    return User.query.get(int(user_id))

# --- Login route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        # Check database users
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main dashboard showing all students"""
    students = Student.query.order_by(Student.name).all()
    students_data = [student.to_dict() for student in students]
    
    # Calculate stats
    total_students = len(students_data)
    all_courses = []
    all_grades = []
    for student in students_data:
        all_courses.extend(student['courses'])
        all_grades.extend(student['grades'])
    
    total_courses = len(set(all_courses))
    avg_grade = sum(all_grades) / len(all_grades) if all_grades else 0
    
    stats = {
        'total_students': total_students,
        'total_courses': total_courses,
        'avg_grade': round(avg_grade, 2)
    }
    
    return render_template('index.html', students=students_data, stats=stats)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        roll_no = request.form['roll_no'].strip()
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        courses_str = request.form['courses'].strip()
        grades_str = request.form['grades'].strip()
        
        # Validate inputs
        if not all([roll_no, name, email, courses_str, grades_str]):
            flash('All fields are required', 'error')
            return render_template('add_student.html')
        
        # Parse courses and grades
        courses = [course.strip() for course in courses_str.split(',')]
        try:
            grades = [float(grade.strip()) for grade in grades_str.split(',')]
        except ValueError:
            flash('Grades must be valid numbers', 'error')
            return render_template('add_student.html')
        
        if len(courses) != len(grades):
            flash('Number of courses must match number of grades', 'error')
            return render_template('add_student.html')
        
        # Check if roll number exists
        existing_student = Student.query.filter_by(roll_no=roll_no).first()
        if existing_student:
            flash('Roll number already exists', 'error')
            return render_template('add_student.html')
        
        # Add student using SQLAlchemy
        try:
            student = Student()
            student.roll_no = roll_no
            student.name = name
            student.email = email
            student.courses = courses
            student.grades = grades
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding student. Please try again.', 'error')
            return render_template('add_student.html')
    
    return render_template('add_student.html')

@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
@login_required
def edit_student(roll_no):
    """Edit an existing student"""
    student = Student.query.filter_by(roll_no=roll_no).first()
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        courses_str = request.form['courses'].strip()
        grades_str = request.form['grades'].strip()
        
        # Validate inputs
        if not all([name, email, courses_str, grades_str]):
            flash('All fields are required', 'error')
            return render_template('edit_student.html', student=student.to_dict())
        
        # Parse courses and grades
        courses = [course.strip() for course in courses_str.split(',')]
        try:
            grades = [float(grade.strip()) for grade in grades_str.split(',')]
        except ValueError:
            flash('Grades must be valid numbers', 'error')
            return render_template('edit_student.html', student=student.to_dict())
        
        if len(courses) != len(grades):
            flash('Number of courses must match number of grades', 'error')
            return render_template('edit_student.html', student=student.to_dict())
        
        # Update student
        try:
            student.name = name
            student.email = email
            student.courses = courses
            student.grades = grades
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student. Please try again.', 'error')
    
    return render_template('edit_student.html', student=student.to_dict())

@app.route('/delete_student/<roll_no>', methods=['POST'])
@login_required
def delete_student(roll_no):
    """Delete a student"""
    student = Student.query.filter_by(roll_no=roll_no).first()
    if student:
        try:
            db.session.delete(student)
            db.session.commit()
            flash('Student deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting student', 'error')
    else:
        flash('Student not found', 'error')
    
    return redirect(url_for('index'))

@app.route('/query', methods=['GET', 'POST'])
@login_required
def query():
    """Custom query interface"""
    results = None
    
    if request.method == 'POST':
        query_text = request.form['query'].strip()
        if query_text:
            try:
                # Security checks for safe queries
                forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
                if any(keyword in query_text.upper() for keyword in forbidden_keywords):
                    flash('Only SELECT queries are allowed', 'error')
                elif len(query_text) > 1000:
                    flash('Query too long (max 1000 characters)', 'error')
                elif query_text.upper().startswith('SELECT'):
                    # Use raw SQL for custom queries
                    result = db.session.execute(text(query_text))
                    results = [list(row) for row in result.fetchall()]
                    # Limit results for display
                    if len(results) > 100:
                        results = results[:100]
                        flash(f'Query executed successfully. Showing first 100 results.', 'success')
                    else:
                        flash(f'Query executed successfully. Found {len(results)} results.', 'success')
                else:
                    flash('Only SELECT queries are allowed', 'error')
            except Exception as e:
                flash(f'Query error: {str(e)}', 'error')
    
    return render_template('query.html', results=results or [])


@app.route('/reports')
@login_required
def reports():
    """Generate reports"""
    try:
        students = Student.query.all()
        students_data = [student.to_dict() for student in students]
        
        total_students = len(students_data)
        
        if total_students == 0:
            flash('No students found to generate reports', 'warning')
            return render_template('reports.html', report_data={})
        
        # Course statistics and grade distribution
        course_stats = {}
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for student_data in students_data:
            courses = student_data['courses']
            grades = student_data['grades']
            
            for course, grade in zip(courses, grades):
                if course not in course_stats:
                    course_stats[course] = {'total_students': 0, 'total_grade': 0, 'avg_grade': 0}
                
                course_stats[course]['total_students'] += 1
                course_stats[course]['total_grade'] += grade
                
                # Grade distribution
                if grade >= 90:
                    grade_distribution['A'] += 1
                elif grade >= 80:
                    grade_distribution['B'] += 1
                elif grade >= 70:
                    grade_distribution['C'] += 1
                elif grade >= 60:
                    grade_distribution['D'] += 1
                else:
                    grade_distribution['F'] += 1
        
        # Calculate averages
        for course in course_stats:
            if course_stats[course]['total_students'] > 0:
                course_stats[course]['avg_grade'] = round(
                    course_stats[course]['total_grade'] / course_stats[course]['total_students'], 2
                )
        
        # Top performers
        top_performers = []
        for student in students:
            avg_grade = student.get_average_grade()
            top_performers.append({
                'name': student.name,
                'roll_no': student.roll_no,
                'avg_grade': avg_grade,
                'courses': student.courses
            })
        
        top_performers.sort(key=lambda x: x['avg_grade'], reverse=True)
        top_performers = top_performers[:5]
        
        # Low performers - students needing attention (all students with avg < 70)
        low_performers = []
        for student in students:
            avg_grade = student.get_average_grade()
            if avg_grade < 70:
                low_performers.append({
                    'name': student.name,
                    'roll_no': student.roll_no,
                    'avg_grade': avg_grade,
                    'courses': student.courses
                })
        
        low_performers.sort(key=lambda x: x['avg_grade'])
        low_performers = low_performers[:10]
        
        # Overall average
        all_grades = []
        for student_data in students_data:
            all_grades.extend(student_data['grades'])
        overall_avg = round(sum(all_grades) / len(all_grades), 2) if all_grades else 0
        
        report_data = {
            'total_students': total_students,
            'total_courses': len(course_stats),
            'overall_avg': overall_avg,
            'course_stats': course_stats,
            'grade_distribution': grade_distribution,
            'top_performers': top_performers,
            'low_performers': low_performers
        }
        
        return render_template('reports.html', report_data=report_data)
        
    except Exception as e:
        flash('An error occurred while generating reports', 'error')
        return redirect(url_for('index'))

@app.route('/search')
@login_required
def search():
    """Search students"""
    search_term = request.args.get('search', '').strip()
    students_data = []
    
    if search_term:
        # Use SQLAlchemy ORM for searching
        students = Student.query.filter(
            or_(
                Student.name.ilike(f'%{search_term}%'),
                Student.roll_no.ilike(f'%{search_term}%'),
                Student.email.ilike(f'%{search_term}%')
            )
        ).all()
        
        students_data = [student.to_dict() for student in students]
    
    return render_template('index.html', students=students_data, search_term=search_term, stats={'total_students': len(students_data), 'total_courses': 0, 'avg_grade': 0})

@app.route('/export')
@login_required
def export():
    """Export students data as JSON"""
    students = Student.query.all()
    students_data = [student.to_dict() for student in students]
    
    # Create JSON response
    json_data = json.dumps(students_data, indent=2, default=str)
    
    return Response(
        json_data,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=students_export.json'}
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)