from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from datetime import datetime, date, time
from flask_login import UserMixin
from enum import Enum

db = SQLAlchemy()

# Enums for various status fields
class AttendanceStatus(Enum):
    PRESENT = 'present'
    ABSENT = 'absent'
    LATE = 'late'
    EXCUSED = 'excused'

class FeeStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'

class BookStatus(Enum):
    AVAILABLE = 'available'
    BORROWED = 'borrowed'
    RESERVED = 'reserved'
    DAMAGED = 'damaged'

class UserRole(Enum):
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'
    PARENT = 'parent'
    STAFF = 'staff'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    courses = db.Column(ARRAY(db.String), nullable=False)
    grades = db.Column(ARRAY(db.Numeric), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Student {self.roll_no}: {self.name}>'
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'id': self.id,
            'roll_no': self.roll_no,
            'name': self.name,
            'email': self.email,
            'courses': self.courses,
            'grades': [float(grade) for grade in self.grades],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_average_grade(self):
        """Calculate average grade for this student"""
        if self.grades:
            return round(sum(float(grade) for grade in self.grades) / len(self.grades), 2)
        return 0.0

# Feature 1: Course Management System
class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(10))
    max_students = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='courses')
    teacher = db.relationship('Teacher', backref='courses')
    
    def __repr__(self):
        return f'<Course {self.course_code}: {self.course_name}>'

# Feature 2: Teacher/Faculty Management
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    date_of_joining = db.Column(db.Date)
    salary = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='teacher_profile')
    department = db.relationship('Department', foreign_keys=[department_id], backref='teachers')
    
    def __repr__(self):
        return f'<Teacher {self.employee_id}: {self.first_name} {self.last_name}>'

# Feature 3: Department Management
class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    department_code = db.Column(db.String(10), unique=True, nullable=False)
    department_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    head_of_department_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    budget = db.Column(db.Numeric(12, 2))
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Department {self.department_code}: {self.department_name}>'

# Feature 4: Semester/Academic Year Management
class AcademicPeriod(db.Model):
    __tablename__ = 'academic_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    academic_year = db.Column(db.String(10), nullable=False)  # e.g., "2023-24"
    semester = db.Column(db.String(20), nullable=False)  # e.g., "Fall", "Spring"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    registration_start = db.Column(db.Date)
    registration_end = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AcademicPeriod {self.academic_year} {self.semester}>'

# Feature 5: Attendance Tracking
class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    notes = db.Column(db.Text)
    marked_by = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='attendance_records')
    course = db.relationship('Course', backref='attendance_records')
    marked_by_teacher = db.relationship('Teacher', backref='attendance_marked')
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date} - {self.status.value}>'

# Feature 6: Enhanced Grade Analytics (Exam Results)
class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=False)
    max_marks = db.Column(db.Numeric(5, 2), nullable=False)
    grade = db.Column(db.String(5))
    percentage = db.Column(db.Numeric(5, 2))
    rank = db.Column(db.Integer)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='exam_results')
    exam = db.relationship('Exam', backref='results')
    course = db.relationship('Course', backref='exam_results')
    
    def __repr__(self):
        return f'<ExamResult {self.student_id} - {self.exam_id} - {self.marks_obtained}/{self.max_marks}>'

# Feature 7: Parent/Guardian Management
class Guardian(db.Model):
    __tablename__ = 'guardians'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # Father, Mother, Guardian, etc.
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    occupation = db.Column(db.String(100))
    workplace = db.Column(db.String(200))
    emergency_contact = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Guardian {self.first_name} {self.last_name} ({self.relationship})>'

# Junction table for Student-Guardian many-to-many relationship
class StudentGuardian(db.Model):
    __tablename__ = 'student_guardians'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardians.id'), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='guardian_relationships')
    guardian = db.relationship('Guardian', backref='student_relationships')

# Feature 8: Fee Management
class FeeType(db.Model):
    __tablename__ = 'fee_types'
    
    id = db.Column(db.Integer, primary_key=True)
    fee_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_mandatory = db.Column(db.Boolean, default=True)
    due_date_offset = db.Column(db.Integer, default=30)  # days from start of semester
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FeeType {self.fee_name}: {self.amount}>'

class StudentFee(db.Model):
    __tablename__ = 'student_fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_type_id = db.Column(db.Integer, db.ForeignKey('fee_types.id'), nullable=False)
    academic_period_id = db.Column(db.Integer, db.ForeignKey('academic_periods.id'), nullable=False)
    amount_due = db.Column(db.Numeric(10, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(FeeStatus), default=FeeStatus.PENDING)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='fees')
    fee_type = db.relationship('FeeType', backref='student_fees')
    academic_period = db.relationship('AcademicPeriod', backref='fees')
    
    def __repr__(self):
        return f'<StudentFee {self.student_id} - {self.fee_type_id} - {self.status.value}>'

# Feature 9: Library Management
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    publisher = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)
    category = db.Column(db.String(100))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    location = db.Column(db.String(100))  # Shelf location
    status = db.Column(db.Enum(BookStatus), default=BookStatus.AVAILABLE)
    purchase_date = db.Column(db.Date)
    price = db.Column(db.Numeric(8, 2))
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Book {self.isbn}: {self.title}>'

class BookBorrowing(db.Model):
    __tablename__ = 'book_borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    borrowed_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date)
    fine_amount = db.Column(db.Numeric(8, 2), default=0)
    notes = db.Column(db.Text)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    book = db.relationship('Book', backref='borrowing_records')
    student = db.relationship('Student', backref='borrowed_books')
    issued_by_user = db.relationship('User', backref='books_issued')
    
    def __repr__(self):
        return f'<BookBorrowing {self.book_id} - {self.student_id} - {self.borrowed_date}>'

# Feature 10: Exam Management
class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # Midterm, Final, Quiz, etc.
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    academic_period_id = db.Column(db.Integer, db.ForeignKey('academic_periods.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer)  # Duration in minutes
    max_marks = db.Column(db.Numeric(5, 2), nullable=False)
    passing_marks = db.Column(db.Numeric(5, 2))
    venue = db.Column(db.String(100))
    instructions = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='exams')
    academic_period = db.relationship('AcademicPeriod', backref='exams')
    
    def __repr__(self):
        return f'<Exam {self.exam_name} - {self.course_id} - {self.exam_date}>'

# Feature 11: Timetable/Schedule Management
class Timetable(db.Model):
    __tablename__ = 'timetables'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    academic_period_id = db.Column(db.Integer, db.ForeignKey('academic_periods.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='timetable_slots')
    teacher = db.relationship('Teacher', backref='timetable_slots')
    room = db.relationship('Room', backref='timetable_slots')
    academic_period = db.relationship('AcademicPeriod', backref='timetables')
    
    def __repr__(self):
        return f'<Timetable {self.course_id} - Day {self.day_of_week} - {self.start_time}>'

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    room_name = db.Column(db.String(100))
    building = db.Column(db.String(100))
    floor = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    room_type = db.Column(db.String(50))  # Classroom, Lab, Auditorium, etc.
    facilities = db.Column(ARRAY(db.String))  # Projector, AC, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Room {self.room_number}: {self.room_name}>'

# Feature 12: Assignment Management
class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    assigned_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    max_marks = db.Column(db.Numeric(5, 2))
    instructions = db.Column(db.Text)
    attachment_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='assignments')
    teacher = db.relationship('Teacher', backref='assignments')
    
    def __repr__(self):
        return f'<Assignment {self.title} - {self.course_id}>'

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text)
    attachment_url = db.Column(db.String(500))
    marks_obtained = db.Column(db.Numeric(5, 2))
    feedback = db.Column(db.Text)
    graded_by = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    graded_at = db.Column(db.DateTime)
    is_late = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment = db.relationship('Assignment', backref='submissions')
    student = db.relationship('Student', backref='assignment_submissions')
    graded_by_teacher = db.relationship('Teacher', backref='graded_assignments')
    
    def __repr__(self):
        return f'<AssignmentSubmission {self.assignment_id} - {self.student_id}>'

# Feature 13: Event/Announcement System
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50))  # Academic, Cultural, Sports, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    venue = db.Column(db.String(200))
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    max_participants = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    registration_deadline = db.Column(db.Date)
    is_public = db.Column(db.Boolean, default=True)
    banner_image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organizer = db.relationship('User', backref='organized_events')
    
    def __repr__(self):
        return f'<Event {self.title} - {self.start_date}>'

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.String(50))  # General, Urgent, Academic, etc.
    target_audience = db.Column(db.String(50))  # All, Students, Teachers, Parents
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    publish_date = db.Column(db.Date, default=date.today)
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # 1=Low, 2=Medium, 3=High
    attachment_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='announcements')
    
    def __repr__(self):
        return f'<Announcement {self.title} - {self.publish_date}>'

# Feature 14: Student Counseling Records
class CounselingSession(db.Model):
    __tablename__ = 'counseling_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    counselor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_type = db.Column(db.String(50))  # Academic, Personal, Career, etc.
    purpose = db.Column(db.String(200))
    notes = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    is_confidential = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='counseling_sessions')
    counselor = db.relationship('User', backref='counseling_sessions')
    
    def __repr__(self):
        return f'<CounselingSession {self.student_id} - {self.session_date}>'

# Feature 15: Disciplinary Actions
class DisciplinaryAction(db.Model):
    __tablename__ = 'disciplinary_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    incident_date = db.Column(db.Date, nullable=False)
    incident_description = db.Column(db.Text, nullable=False)
    action_type = db.Column(db.String(50))  # Warning, Suspension, Fine, etc.
    action_description = db.Column(db.Text)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    action_taken_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    severity_level = db.Column(db.Integer)  # 1=Minor, 2=Major, 3=Severe
    penalty_amount = db.Column(db.Numeric(8, 2))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='disciplinary_actions')
    reported_by_user = db.relationship('User', foreign_keys=[reported_by], backref='reported_incidents')
    action_by_user = db.relationship('User', foreign_keys=[action_taken_by], backref='handled_incidents')
    
    def __repr__(self):
        return f'<DisciplinaryAction {self.student_id} - {self.incident_date}>'

# Feature 16: Transportation Management
class TransportRoute(db.Model):
    __tablename__ = 'transport_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    route_number = db.Column(db.String(20), unique=True, nullable=False)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    vehicle_number = db.Column(db.String(20))
    vehicle_capacity = db.Column(db.Integer)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    stops = db.Column(ARRAY(db.String))  # Array of stop names
    monthly_fee = db.Column(db.Numeric(8, 2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TransportRoute {self.route_number}: {self.route_name}>'

class StudentTransport(db.Model):
    __tablename__ = 'student_transport'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'), nullable=False)
    pickup_stop = db.Column(db.String(100))
    drop_stop = db.Column(db.String(100))
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='transport_details')
    route = db.relationship('TransportRoute', backref='students')
    
    def __repr__(self):
        return f'<StudentTransport {self.student_id} - {self.route_id}>'

# Feature 17: Hostel/Dormitory Management
class Hostel(db.Model):
    __tablename__ = 'hostels'
    
    id = db.Column(db.Integer, primary_key=True)
    hostel_name = db.Column(db.String(100), nullable=False)
    hostel_type = db.Column(db.String(20))  # Boys, Girls, Mixed
    warden_name = db.Column(db.String(100))
    warden_phone = db.Column(db.String(20))
    total_rooms = db.Column(db.Integer)
    occupied_rooms = db.Column(db.Integer, default=0)
    address = db.Column(db.Text)
    facilities = db.Column(ARRAY(db.String))
    monthly_fee = db.Column(db.Numeric(8, 2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Hostel {self.hostel_name} ({self.hostel_type})>'

class HostelRoom(db.Model):
    __tablename__ = 'hostel_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'), nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(20))  # Single, Double, Triple
    max_occupancy = db.Column(db.Integer)
    current_occupancy = db.Column(db.Integer, default=0)
    monthly_rent = db.Column(db.Numeric(8, 2))
    facilities = db.Column(ARRAY(db.String))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    hostel = db.relationship('Hostel', backref='rooms')
    
    def __repr__(self):
        return f'<HostelRoom {self.hostel_id}-{self.room_number}>'

class StudentHostel(db.Model):
    __tablename__ = 'student_hostel'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('hostel_rooms.id'), nullable=False)
    check_in_date = db.Column(db.Date, default=date.today)
    check_out_date = db.Column(db.Date)
    emergency_contact = db.Column(db.String(20))
    special_requirements = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='hostel_details')
    room = db.relationship('HostelRoom', backref='residents')
    
    def __repr__(self):
        return f'<StudentHostel {self.student_id} - {self.room_id}>'

# Feature 18: Health Records
class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    visit_date = db.Column(db.Date, default=date.today)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    doctor_name = db.Column(db.String(100))
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    allergies = db.Column(db.Text)
    blood_group = db.Column(db.String(5))
    height = db.Column(db.Numeric(5, 2))  # in cm
    weight = db.Column(db.Numeric(5, 2))  # in kg
    is_confidential = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='health_records')
    
    def __repr__(self):
        return f'<HealthRecord {self.student_id} - {self.visit_date}>'

# Feature 19: Scholarship Management
class Scholarship(db.Model):
    __tablename__ = 'scholarships'
    
    id = db.Column(db.Integer, primary_key=True)
    scholarship_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    scholarship_type = db.Column(db.String(50))  # Merit, Need-based, Sports, etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    eligibility_criteria = db.Column(db.Text)
    application_deadline = db.Column(db.Date)
    academic_year = db.Column(db.String(10))
    max_recipients = db.Column(db.Integer)
    current_recipients = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Scholarship {self.scholarship_name} - {self.amount}>'

class ScholarshipApplication(db.Model):
    __tablename__ = 'scholarship_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarships.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    application_date = db.Column(db.Date, default=date.today)
    application_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    documents_submitted = db.Column(ARRAY(db.String))
    essay = db.Column(db.Text)
    recommendation_letters = db.Column(db.Integer, default=0)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_date = db.Column(db.Date)
    review_comments = db.Column(db.Text)
    disbursement_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scholarship = db.relationship('Scholarship', backref='applications')
    student = db.relationship('Student', backref='scholarship_applications')
    reviewer = db.relationship('User', backref='scholarship_reviews')
    
    def __repr__(self):
        return f'<ScholarshipApplication {self.scholarship_id} - {self.student_id}>'

# Feature 20: Alumni Management
class Alumni(db.Model):
    __tablename__ = 'alumni'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    graduation_year = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(100))
    current_designation = db.Column(db.String(100))
    current_company = db.Column(db.String(200))
    current_address = db.Column(db.Text)
    current_phone = db.Column(db.String(20))
    current_email = db.Column(db.String(120))
    linkedin_profile = db.Column(db.String(200))
    achievements = db.Column(db.Text)
    willing_to_mentor = db.Column(db.Boolean, default=False)
    industry = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='alumni_record')
    
    def __repr__(self):
        return f'<Alumni {self.graduation_year} - {self.current_company}>'

# Feature 21: Staff Management (Non-teaching)
class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    date_of_joining = db.Column(db.Date)
    salary = db.Column(db.Numeric(10, 2))
    skills = db.Column(ARRAY(db.String))
    shift_timing = db.Column(db.String(50))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='staff_profile')
    supervisor = db.relationship('Staff', remote_side=[id], backref='subordinates')
    
    def __repr__(self):
        return f'<Staff {self.employee_id}: {self.first_name} {self.last_name}>'

# Feature 22: Inventory Management
class InventoryCategory(db.Model):
    __tablename__ = 'inventory_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<InventoryCategory {self.category_name}>'

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'))
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    minimum_quantity = db.Column(db.Integer, default=5)
    unit_price = db.Column(db.Numeric(10, 2))
    supplier = db.Column(db.String(200))
    location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    category = db.relationship('InventoryCategory', backref='items')
    
    def __repr__(self):
        return f'<InventoryItem {self.item_code}: {self.item_name}>'

# Feature 23: Communication/Messages
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='general')  # general, urgent, academic
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    attachment_url = db.Column(db.String(500))
    parent_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))  # For replies
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    parent_message = db.relationship('Message', remote_side=[id], backref='replies')
    
    def __repr__(self):
        return f'<Message {self.sender_id} -> {self.recipient_id}: {self.subject}>'

# Feature 24: Reports and Analytics
class ReportTemplate(db.Model):
    __tablename__ = 'report_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(50))  # student, financial, academic, etc.
    sql_query = db.Column(db.Text)
    parameters = db.Column(JSON)  # JSON field for dynamic parameters
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='report_templates')
    
    def __repr__(self):
        return f'<ReportTemplate {self.template_name}>'

# Feature 25: Certificates and Documents
class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    certificate_type = db.Column(db.String(100), nullable=False)  # Graduation, Course Completion, etc.
    certificate_number = db.Column(db.String(100), unique=True, nullable=False)
    issue_date = db.Column(db.Date, default=date.today)
    valid_until = db.Column(db.Date)
    issuing_authority = db.Column(db.String(200))
    description = db.Column(db.Text)
    digital_signature = db.Column(db.String(500))
    verification_code = db.Column(db.String(100))
    file_url = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='certificates')
    
    def __repr__(self):
        return f'<Certificate {self.certificate_number}: {self.certificate_type}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(100))  # ID Card, Transcript, etc.
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_type = db.Column(db.String(20))  # student, teacher, staff
    file_url = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    mime_type = db.Column(db.String(100))
    upload_date = db.Column(db.Date, default=date.today)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.Date)
    verification_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_documents')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_documents')
    
    def __repr__(self):
        return f'<Document {self.document_name} - {self.owner_type}>'