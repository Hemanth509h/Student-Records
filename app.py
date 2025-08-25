import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from student_manager import StudentManager
from query_engine import QueryEngine
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize managers
student_manager = StudentManager()
query_engine = QueryEngine(student_manager)

@app.route('/')
def index():
    """Main dashboard showing all students"""
    students = student_manager.get_all_students()
    stats = {
        'total_students': len(students),
        'total_courses': len(set(course for student in students for course in student.get('courses', []))),
        'avg_grade': student_manager.calculate_average_grade()
    }
    return render_template('index.html', students=students, stats=stats)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        try:
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
            
            # Create student data
            student_data = {
                'roll_no': roll_no,
                'name': name,
                'email': email,
                'courses': courses,
                'grades': grades
            }
            
            success = student_manager.add_student(student_data)
            if success:
                flash(f'Student {name} added successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Roll number already exists', 'error')
                
        except Exception as e:
            logging.error(f"Error adding student: {e}")
            flash('An error occurred while adding the student', 'error')
    
    return render_template('add_student.html')

@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
def edit_student(roll_no):
    """Edit an existing student"""
    student = student_manager.get_student(roll_no)
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            courses_str = request.form['courses'].strip()
            grades_str = request.form['grades'].strip()
            
            # Validate inputs
            if not all([name, email, courses_str, grades_str]):
                flash('All fields are required', 'error')
                return render_template('edit_student.html', student=student)
            
            # Parse courses and grades
            courses = [course.strip() for course in courses_str.split(',')]
            try:
                grades = [float(grade.strip()) for grade in grades_str.split(',')]
            except ValueError:
                flash('Grades must be valid numbers', 'error')
                return render_template('edit_student.html', student=student)
            
            if len(courses) != len(grades):
                flash('Number of courses must match number of grades', 'error')
                return render_template('edit_student.html', student=student)
            
            # Update student data
            updated_data = {
                'roll_no': roll_no,
                'name': name,
                'email': email,
                'courses': courses,
                'grades': grades
            }
            
            student_manager.update_student(roll_no, updated_data)
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logging.error(f"Error updating student: {e}")
            flash('An error occurred while updating the student', 'error')
    
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<roll_no>')
def delete_student(roll_no):
    """Delete a student"""
    student = student_manager.get_student(roll_no)
    if student:
        student_manager.delete_student(roll_no)
        flash(f'Student {student["name"]} deleted successfully!', 'success')
    else:
        flash('Student not found', 'error')
    return redirect(url_for('index'))

@app.route('/query', methods=['GET', 'POST'])
def query():
    """SQL-like query interface"""
    results = []
    query_text = ""
    
    if request.method == 'POST':
        query_text = request.form['query'].strip()
        if query_text:
            try:
                results = query_engine.execute_query(query_text)
                flash(f'Query executed successfully. Found {len(results)} results.', 'success')
            except Exception as e:
                flash(f'Query error: {str(e)}', 'error')
                results = []
    
    return render_template('query.html', results=results, query_text=query_text)

@app.route('/reports')
def reports():
    """Generate reports and statistics"""
    try:
        # Get all students for processing
        all_students = student_manager.get_all_students()
        
        # Calculate statistics
        total_students = len(all_students)
        
        # Course-wise statistics
        course_stats = {}
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for student in all_students:
            courses = student.get('courses', [])
            grades = student.get('grades', [])
            
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
        top_performers = student_manager.get_top_performers(5)
        
        # Students needing attention (average < 70)
        low_performers = []
        for student in all_students:
            grades = student.get('grades', [])
            if grades:
                avg_grade = sum(grades) / len(grades)
                if avg_grade < 70:
                    student_copy = student.copy()
                    student_copy['avg_grade'] = round(avg_grade, 2)
                    low_performers.append(student_copy)
        
        # Sort low performers by average grade
        low_performers.sort(key=lambda x: x['avg_grade'])
        
        report_data = {
            'total_students': total_students,
            'total_courses': len(course_stats),
            'overall_avg': student_manager.calculate_average_grade(),
            'course_stats': course_stats,
            'grade_distribution': grade_distribution,
            'top_performers': top_performers,
            'low_performers': low_performers[:10]  # Top 10 students needing attention
        }
        
        return render_template('reports.html', report_data=report_data)
        
    except Exception as e:
        logging.error(f"Error generating reports: {e}")
        flash('An error occurred while generating reports', 'error')
        return redirect(url_for('index'))

@app.route('/search')
def search():
    """Search students"""
    search_term = request.args.get('search', '').strip()
    students = []
    
    if search_term:
        students = student_manager.search_students(search_term)
        flash(f'Found {len(students)} students matching "{search_term}"', 'info')
    
    return render_template('index.html', students=students, search_term=search_term)

@app.route('/export')
def export_data():
    """Export student data as JSON"""
    try:
        students = student_manager.get_all_students()
        
        # Create response with JSON data
        from flask import Response
        import json
        
        json_data = json.dumps(students, indent=2)
        
        response = Response(
            json_data,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=student_records.json'}
        )
        
        flash('Student data exported successfully!', 'success')
        return response
        
    except Exception as e:
        logging.error(f"Error exporting data: {e}")
        flash('An error occurred while exporting data', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
