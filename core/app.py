import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Database connection
def get_db():
    return psycopg2.connect(os.environ['DATABASE_URL'])

@app.route('/')
def index():
    """Main dashboard showing all students"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get all students
    cur.execute("SELECT roll_no, name, email, courses, grades FROM students ORDER BY name")
    rows = cur.fetchall()
    
    students = []
    for row in rows:
        students.append({
            'roll_no': row[0],
            'name': row[1], 
            'email': row[2],
            'courses': row[3],
            'grades': row[4]
        })
    
    # Calculate stats
    total_students = len(students)
    all_courses = []
    all_grades = []
    for student in students:
        all_courses.extend(student['courses'])
        all_grades.extend(student['grades'])
    
    total_courses = len(set(all_courses))
    avg_grade = sum(all_grades) / len(all_grades) if all_grades else 0
    
    stats = {
        'total_students': total_students,
        'total_courses': total_courses,
        'avg_grade': round(avg_grade, 2)
    }
    
    cur.close()
    conn.close()
    return render_template('index.html', students=students, stats=stats)

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
        
        # Add to database
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO students (roll_no, name, email, courses, grades) VALUES (%s, %s, %s, %s, %s)",
                (roll_no, name, email, courses, grades)
            )
            conn.commit()
            flash(f'Student {name} added successfully!', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('index'))
        except psycopg2.IntegrityError:
            flash('Roll number already exists', 'error')
            cur.close()
            conn.close()
    
    return render_template('add_student.html')

@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
def edit_student(roll_no):
    """Edit an existing student"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get student
    cur.execute("SELECT roll_no, name, email, courses, grades FROM students WHERE roll_no = %s", (roll_no,))
    row = cur.fetchone()
    
    if not row:
        flash('Student not found', 'error')
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    
    student = {
        'roll_no': row[0],
        'name': row[1],
        'email': row[2], 
        'courses': row[3],
        'grades': row[4]
    }
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        courses_str = request.form['courses'].strip()
        grades_str = request.form['grades'].strip()
        
        # Validate inputs
        if not all([name, email, courses_str, grades_str]):
            flash('All fields are required', 'error')
            cur.close()
            conn.close()
            return render_template('edit_student.html', student=student)
        
        # Parse courses and grades
        courses = [course.strip() for course in courses_str.split(',')]
        try:
            grades = [float(grade.strip()) for grade in grades_str.split(',')]
        except ValueError:
            flash('Grades must be valid numbers', 'error')
            cur.close()
            conn.close()
            return render_template('edit_student.html', student=student)
        
        if len(courses) != len(grades):
            flash('Number of courses must match number of grades', 'error')
            cur.close()
            conn.close()
            return render_template('edit_student.html', student=student)
        
        # Update in database
        cur.execute(
            "UPDATE students SET name = %s, email = %s, courses = %s, grades = %s WHERE roll_no = %s",
            (name, email, courses, grades, roll_no)
        )
        conn.commit()
        flash(f'Student {name} updated successfully!', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    
    cur.close()
    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<roll_no>')
def delete_student(roll_no):
    """Delete a student"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get student name first
    cur.execute("SELECT name FROM students WHERE roll_no = %s", (roll_no,))
    row = cur.fetchone()
    
    if row:
        # Delete student
        cur.execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
        conn.commit()
        flash(f'Student {row[0]} deleted successfully!', 'success')
    else:
        flash('Student not found', 'error')
    
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/query', methods=['GET', 'POST'])
def query():
    """SQL query interface"""
    results = []
    query_text = ""
    
    if request.method == 'POST':
        query_text = request.form['query'].strip()
        if query_text:
            conn = get_db()
            cur = conn.cursor()
            try:
                # Simple query processing
                if query_text.upper().startswith('SELECT'):
                    cur.execute(query_text)
                    rows = cur.fetchall()
                    results = [list(row) for row in rows]
                    flash(f'Query executed successfully. Found {len(results)} results.', 'success')
                else:
                    flash('Only SELECT queries are allowed', 'error')
            except Exception as e:
                flash(f'Query error: {str(e)}', 'error')
            finally:
                cur.close()
                conn.close()
    
    return render_template('query.html', results=results, query_text=query_text)

@app.route('/reports')
def reports():
    """Generate reports and statistics"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get all students
    cur.execute("SELECT name, courses, grades FROM students")
    rows = cur.fetchall()
    
    total_students = len(rows)
    
    # Calculate course stats
    course_stats = {}
    grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    
    for row in rows:
        name, courses, grades = row
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
    cur.execute("""
        SELECT name, roll_no, 
               (SELECT AVG(unnest) FROM unnest(grades)) as avg_grade 
        FROM students 
        ORDER BY (SELECT AVG(unnest) FROM unnest(grades)) DESC 
        LIMIT 5
    """)
    top_performers = []
    for row in cur.fetchall():
        top_performers.append({
            'name': row[0],
            'roll_no': row[1], 
            'avg_grade': round(float(row[2]), 2)
        })
    
    # Low performers
    cur.execute("""
        SELECT name, roll_no,
               (SELECT AVG(unnest) FROM unnest(grades)) as avg_grade
        FROM students 
        WHERE (SELECT AVG(unnest) FROM unnest(grades)) < 70
        ORDER BY (SELECT AVG(unnest) FROM unnest(grades)) ASC
        LIMIT 10
    """)
    low_performers = []
    for row in cur.fetchall():
        low_performers.append({
            'name': row[0],
            'roll_no': row[1],
            'avg_grade': round(float(row[2]), 2)
        })
    
    # Overall average
    cur.execute("SELECT AVG(unnest) FROM (SELECT unnest(grades) FROM students) as all_grades")
    result = cur.fetchone()
    overall_avg = round(float(result[0]), 2) if result and result[0] else 0
    
    report_data = {
        'total_students': total_students,
        'total_courses': len(course_stats),
        'overall_avg': overall_avg,
        'course_stats': course_stats,
        'grade_distribution': grade_distribution,
        'top_performers': top_performers,
        'low_performers': low_performers
    }
    
    cur.close()
    conn.close()
    return render_template('reports.html', report_data=report_data)

@app.route('/search')
def search():
    """Search students"""
    search_term = request.args.get('search', '').strip()
    
    if search_term:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT roll_no, name, email, courses, grades FROM students WHERE name ILIKE %s OR roll_no ILIKE %s OR email ILIKE %s",
            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')
        )
        rows = cur.fetchall()
        
        students = []
        for row in rows:
            students.append({
                'roll_no': row[0],
                'name': row[1],
                'email': row[2], 
                'courses': row[3],
                'grades': row[4]
            })
        
        flash(f'Found {len(students)} students matching "{search_term}"', 'info')
        cur.close()
        conn.close()
    else:
        students = []
    
    return render_template('index.html', students=students, search_term=search_term)

@app.route('/export')
def export_data():
    """Export student data as JSON"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT roll_no, name, email, courses, grades FROM students")
    rows = cur.fetchall()
    
    students = []
    for row in rows:
        students.append({
            'roll_no': row[0],
            'name': row[1],
            'email': row[2],
            'courses': row[3], 
            'grades': row[4]
        })
    
    from flask import Response
    import json
    
    json_data = json.dumps(students, indent=2)
    
    response = Response(
        json_data,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=student_records.json'}
    )
    
    flash('Student data exported successfully!', 'success')
    cur.close()
    conn.close()
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)