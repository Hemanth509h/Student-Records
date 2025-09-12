import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from models import db, Student
from student_repository import StudentRepository
from sqlalchemy_repo import SQLAlchemyStudentRepository
from psycopg2_repo import Psycopg2StudentRepository
import json

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    # Generate a random secret for development only
    app.secret_key = secrets.token_hex(32)
    print("WARNING: Using generated secret key for development. Set SESSION_SECRET environment variable in production.")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///student_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Database initialization function
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()

# Initialize repository based on DB_DRIVER environment variable
DB_DRIVER = os.environ.get('DB_DRIVER', 'sqlalchemy').lower()
repository = None

def init_repository():
    """Initialize the appropriate repository based on DB_DRIVER"""
    global repository
    
    if DB_DRIVER == 'psycopg2':
        print(f"Initializing psycopg2 repository with driver: {DB_DRIVER}")
        repository = Psycopg2StudentRepository()
        try:
            repository.initialize_database()
            print("psycopg2 repository initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize psycopg2 database: {e}")
    else:
        print(f"Initializing SQLAlchemy repository with driver: {DB_DRIVER}")
        repository = SQLAlchemyStudentRepository()
        try:
            init_db()  # Initialize SQLAlchemy database
            print("SQLAlchemy repository initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize SQLAlchemy database: {e}")
    
    return repository

def get_average_grade(grades):
    """Calculate average grade from a list of grades"""
    if grades:
        return round(sum(float(grade) for grade in grades) / len(grades), 2)
    return 0.0

# Initialize repository on startup
try:
    init_repository()
except Exception as e:
    print(f"Warning: Could not initialize repository: {e}")
    print("Repository will be initialized on first use")

@app.route('/')
def index():
    """Main dashboard showing all students"""
    students_data = repository.get_all_students()
    # Sort by name since repository may not guarantee order
    students_data.sort(key=lambda x: x['name'])
    
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
        if repository.get_student_by_roll(roll_no):
            flash('Roll number already exists', 'error')
            return render_template('add_student.html')
        
        # Create new student
        if repository.add_student(roll_no, name, email, courses, grades):
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('An error occurred while adding the student', 'error')
    
    return render_template('add_student.html')

@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
def edit_student(roll_no):
    """Edit an existing student"""
    student_data = repository.get_student_by_roll(roll_no)
    if not student_data:
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
            return render_template('edit_student.html', student=student_data)
        
        # Parse courses and grades
        courses = [course.strip() for course in courses_str.split(',')]
        try:
            grades = [float(grade.strip()) for grade in grades_str.split(',')]
        except ValueError:
            flash('Grades must be valid numbers', 'error')
            return render_template('edit_student.html', student=student_data)
        
        if len(courses) != len(grades):
            flash('Number of courses must match number of grades', 'error')
            return render_template('edit_student.html', student=student_data)
        
        # Update student
        if repository.update_student(roll_no, name, email, courses, grades):
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('An error occurred while updating the student', 'error')
    
    return render_template('edit_student.html', student=student_data)

@app.route('/delete_student/<roll_no>')
def delete_student(roll_no):
    """Delete a student"""
    student_data = repository.get_student_by_roll(roll_no)
    if student_data:
        if repository.delete_student(roll_no):
            flash(f'Student {student_data["name"]} deleted successfully!', 'success')
        else:
            flash('An error occurred while deleting the student', 'error')
    else:
        flash('Student not found', 'error')
    
    return redirect(url_for('index'))

@app.route('/query', methods=['GET', 'POST'])
def query():
    """SQL query interface"""
    results = []
    query_text = ""
    
    if request.method == 'POST':
        query_text = request.form['query'].strip()
        if query_text:
            try:
                # Enhanced security for SQL queries
                query_upper = query_text.upper().strip()
                if query_upper.startswith('SELECT') and not any(dangerous in query_upper for dangerous in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']):
                    # Limit query length for security
                    if len(query_text) > 1000:
                        flash('Query too long. Maximum 1000 characters allowed.', 'error')
                    else:
                        # Use repository for custom queries
                        raw_results = repository.execute_select_query(query_text)
                        
                        # Convert raw results to a simple table format for display
                        if raw_results:
                            # Create simple table results
                            results = []
                            for row in raw_results[:100]:  # Limit to 100 rows
                                row_dict = {}
                                for i, value in enumerate(row):
                                    row_dict[f'col_{i}'] = value
                                results.append(row_dict)
                            
                            if len(raw_results) > 100:
                                flash(f'Query executed successfully. Showing first 100 of {len(raw_results)} results.', 'info')
                            else:
                                flash(f'Query executed successfully. Found {len(raw_results)} results.', 'success')
                        else:
                            results = []
                            flash('Query executed successfully. No results found.', 'info')
                else:
                    flash('Only SELECT queries are allowed. No DDL/DML operations permitted.', 'error')
            except Exception as e:
                flash(f'Query error: {str(e)}', 'error')
    
    return render_template('query.html', results=results, query_text=query_text)

@app.route('/reports')
def reports():
    """Generate reports and statistics"""
    try:
        # Get all students
        students_data = repository.get_all_students()
        
        total_students = len(students_data)
        
        # Calculate course stats
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
        for student_data in students_data:
            avg_grade = get_average_grade(student_data['grades'])
            top_performers.append({
                'name': student_data['name'],
                'roll_no': student_data['roll_no'],
                'avg_grade': avg_grade,
                'courses': student_data['courses']
            })
        
        top_performers.sort(key=lambda x: x['avg_grade'], reverse=True)
        top_performers = top_performers[:5]
        
        # Low performers - students needing attention (all students with avg < 70)
        low_performers = []
        for student_data in students_data:
            avg_grade = get_average_grade(student_data['grades'])
            if avg_grade < 70:
                low_performers.append({
                    'name': student_data['name'],
                    'roll_no': student_data['roll_no'],
                    'avg_grade': avg_grade,
                    'courses': student_data['courses']
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
def search():
    """Search students"""
    search_term = request.args.get('search', '').strip()
    students_data = []
    
    if search_term:
        # Use repository for searching
        students_data = repository.search_students(search_term)
        flash(f'Found {len(students_data)} students matching "{search_term}"', 'info')
    
    return render_template('index.html', students=students_data, search_term=search_term)

@app.route('/export')
def export_data():
    """Export student data as JSON"""
    try:
        students_data = repository.get_all_students()
        
        json_data = json.dumps(students_data, indent=2, default=str)
        
        response = Response(
            json_data,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=student_records.json'}
        )
        
        flash('Student data exported successfully!', 'success')
        return response
        
    except Exception as e:
        flash('An error occurred while exporting data', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)