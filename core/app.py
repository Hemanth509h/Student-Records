import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from models import db, Student
import json

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/student_management')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
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
        if Student.query.filter_by(roll_no=roll_no).first():
            flash('Roll number already exists', 'error')
            return render_template('add_student.html')
        
        # Create new student
        try:
            new_student = Student(
                roll_no=roll_no,
                name=name,
                email=email,
                courses=courses,
                grades=grades
            )
            db.session.add(new_student)
            db.session.commit()
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the student', 'error')
    
    return render_template('add_student.html')

@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
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
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the student', 'error')
    
    return render_template('edit_student.html', student=student.to_dict())

@app.route('/delete_student/<roll_no>')
def delete_student(roll_no):
    """Delete a student"""
    student = Student.query.filter_by(roll_no=roll_no).first()
    if student:
        try:
            db.session.delete(student)
            db.session.commit()
            flash(f'Student {student.name} deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
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
                # Simple query processing with SQLAlchemy
                if query_text.upper().startswith('SELECT'):
                    # Use raw SQL for custom queries
                    result = db.session.execute(db.text(query_text))
                    results = [list(row) for row in result]
                    flash(f'Query executed successfully. Found {len(results)} results.', 'success')
                else:
                    flash('Only SELECT queries are allowed', 'error')
            except Exception as e:
                flash(f'Query error: {str(e)}', 'error')
    
    return render_template('query.html', results=results, query_text=query_text)

@app.route('/reports')
def reports():
    """Generate reports and statistics"""
    try:
        # Get all students
        students = Student.query.all()
        students_data = [student.to_dict() for student in students]
        
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
        
        # Low performers
        low_performers = [p for p in top_performers if p['avg_grade'] < 70]
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
        # Use SQLAlchemy ORM for searching
        students = Student.query.filter(
            db.or_(
                Student.name.ilike(f'%{search_term}%'),
                Student.roll_no.ilike(f'%{search_term}%'),
                Student.email.ilike(f'%{search_term}%')
            )
        ).all()
        
        students_data = [student.to_dict() for student in students]
        flash(f'Found {len(students_data)} students matching "{search_term}"', 'info')
    
    return render_template('index.html', students=students_data, search_term=search_term)

@app.route('/export')
def export_data():
    """Export student data as JSON"""
    try:
        students = Student.query.all()
        students_data = [student.to_dict() for student in students]
        
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