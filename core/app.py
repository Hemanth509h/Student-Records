import os
import secrets
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, Response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email_validator import validate_email, EmailNotValidError
from core.models import db, Student, User
from sqlalchemy import text, or_
import json
from PIL import Image
import imghdr

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configure for proxy environments (like Replit) if needed
if os.environ.get('REPLIT_DB_URL') or os.environ.get('REPL_ID'):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    # Generate a random secret for development only
    app.secret_key = secrets.token_hex(32)
    print("WARNING: Using generated secret key for development. Set SESSION_SECRET environment variable in production.")

# Database configuration - PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/postgres')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['PROFILE_UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROFILE_UPLOAD_FOLDER'], exist_ok=True)

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
    
# Hardcoded admin user
class AdminUser(UserMixin):
    def __init__(self):
        self.id = 1
        self.email = "admin@studentrecords.com"

admin_user = AdminUser()

# File upload utility functions
def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(stream):
    """Validate that uploaded file is a valid image"""
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return False
    return format.lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(400, 400)):
    """Resize image to specified maximum size while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save the resized image
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

def save_profile_photo(file, student_roll_no):
    """Save uploaded profile photo and return filename"""
    if file and allowed_file(file.filename):
        # Validate image
        if not validate_image(file.stream):
            return None
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{student_roll_no}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Save file
        file_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Resize image
        if resize_image(file_path):
            return filename
        else:
            # Remove file if resize failed
            try:
                os.remove(file_path)
            except:
                pass
            return None
    return None

def delete_profile_photo(filename):
    """Delete profile photo file"""
    if filename:
        try:
            file_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting profile photo: {e}")

@login_manager.user_loader
def load_user(user_id):
    # Support both hardcoded admin and DB users
    if str(user_id) == "1":
        return admin_user
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

        # Hardcoded admin login
        if email == "admin@studentrecords.com" and password == "admin123":
            login_user(admin_user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        # Database users (if you want to allow them)
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
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
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        date_of_birth_str = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_phone = request.form.get('guardian_phone', '').strip()
        courses_str = request.form['courses'].strip()
        grades_str = request.form['grades'].strip()
        
        # Validate required inputs
        if not all([roll_no, name, email, courses_str, grades_str]):
            flash('Roll number, name, email, courses, and grades are required', 'error')
            return render_template('add_student.html')
        
        # Parse date of birth
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth', 'error')
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
            student.phone = phone
            student.address = address
            student.date_of_birth = date_of_birth
            student.gender = gender
            student.guardian_name = guardian_name
            student.guardian_phone = guardian_phone
            student.courses = courses
            student.grades = grades
            
            # Handle profile photo upload
            profile_photo = request.files.get('profile_photo')
            if profile_photo and profile_photo.filename != '':
                filename = save_profile_photo(profile_photo, roll_no)
                if filename:
                    student.profile_photo = filename
                else:
                    flash('Invalid image file. Please upload a valid image (PNG, JPG, JPEG, GIF, WebP).', 'warning')
            
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
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        date_of_birth_str = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_phone = request.form.get('guardian_phone', '').strip()
        courses_str = request.form['courses'].strip()
        grades_str = request.form['grades'].strip()
        
        # Validate required inputs
        if not all([name, email, courses_str, grades_str]):
            flash('Name, email, courses, and grades are required', 'error')
            return render_template('edit_student.html', student=student.to_dict())
        
        # Parse date of birth
        date_of_birth = None
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth', 'error')
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
            old_photo = student.profile_photo  # Keep track of old photo for deletion
            
            student.name = name
            student.email = email
            student.phone = phone
            student.address = address
            student.date_of_birth = date_of_birth
            student.gender = gender
            student.guardian_name = guardian_name
            student.guardian_phone = guardian_phone
            student.courses = courses
            student.grades = grades
            
            # Handle profile photo upload
            profile_photo = request.files.get('profile_photo')
            if profile_photo and profile_photo.filename != '':
                filename = save_profile_photo(profile_photo, student.roll_no)
                if filename:
                    # Delete old photo if it exists
                    if old_photo:
                        delete_profile_photo(old_photo)
                    student.profile_photo = filename
                else:
                    flash('Invalid image file. Please upload a valid image (PNG, JPG, JPEG, GIF, WebP).', 'warning')
            
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
        
        return render_template('coming_soon.html', report_data=report_data)
        
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