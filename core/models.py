# Import SQLAlchemy for database operations and ORM functionality
from flask_sqlalchemy import SQLAlchemy
# Import datetime for timestamp handling in database records
from datetime import datetime
# Import UserMixin to add authentication-related methods to User model
from flask_login import UserMixin
# Import Enum for creating enumerated constant values for user roles
from enum import Enum

# Create a SQLAlchemy database instance that will be used across the application
db = SQLAlchemy()

# Define an enumeration class to represent different user roles in the system
class UserRole(Enum):
    ADMIN = 'admin'  # Administrator role with full system access
    TEACHER = 'teacher'  # Teacher role for instructors
    STUDENT = 'student'  # Student role for enrolled students
    PARENT = 'parent'  # Parent role for guardians/parents
    STAFF = 'staff'  # Staff role for administrative staff

# Define the User model for user authentication and profile management
# UserMixin adds authentication methods like is_authenticated, is_active, etc.
# db.Model makes this class a database table
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly set the table name in the database
    
    # Primary key: unique identifier for each user (auto-incrementing integer)
    id = db.Column(db.Integer, primary_key=True)
    
    # Email field: unique, required, indexed for fast lookup during login
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Username field: optional display name for the user
    username = db.Column(db.String(80), nullable=True)
    
    # Password hash: stores the hashed password (never store plain text passwords)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role field: defines user permissions (admin, teacher, student, parent, staff)
    # Uses String type instead of Enum for better SQLite compatibility
    role = db.Column(db.String(20), default='student')
    
    # First name: user's first name
    first_name = db.Column(db.String(100))
    
    # Last name: user's last name
    last_name = db.Column(db.String(100))
    
    # Phone: contact phone number
    phone = db.Column(db.String(20))
    
    # Active flag: indicates if the user account is active/enabled
    active = db.Column(db.Boolean, default=True)
    
    # Last login: timestamp of the user's most recent login
    last_login = db.Column(db.DateTime)
    
    # Profile picture: URL or path to user's profile picture
    profile_picture = db.Column(db.String(200))
    
    # Created at: timestamp when the user account was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Updated at: timestamp when the user record was last modified
    # onupdate automatically updates this field when the record changes
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Property required by Flask-Login to check if user account is active
    @property
    def is_active(self):
        return self.active  # Returns the active status of the user
    
    # String representation of the User object for debugging and logging
    def __repr__(self):
        return f'<User {self.email}>'  # Display user's email when object is printed

# Define the Student model for storing student information and academic records
class Student(db.Model):
    __tablename__ = 'students'  # Explicitly set the table name in the database
    
    # Primary key: unique identifier for each student (auto-incrementing integer)
    id = db.Column(db.Integer, primary_key=True)
    
    # Roll number: unique student ID/enrollment number (required, must be unique)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    
    # Name: student's full name (required field)
    name = db.Column(db.String(100), nullable=False)
    
    # Email: student's email address (required field)
    email = db.Column(db.String(100), nullable=False)
    
    # Courses: list of courses the student is enrolled in (stored as JSON for SQLite compatibility)
    # JSON format allows storing arrays in SQLite which doesn't have native array support
    courses = db.Column(db.JSON, nullable=False)
    
    # Grades: list of grades corresponding to each course (stored as JSON for SQLite compatibility)
    # Each grade corresponds to the course at the same index in the courses list
    grades = db.Column(db.JSON, nullable=False)
    
    # Created at: timestamp when the student record was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # String representation of the Student object for debugging and logging
    def __repr__(self):
        return f'<Student {self.roll_no}: {self.name}>'  # Display roll number and name
    
    # Convert student object to dictionary format for JSON serialization
    # Used when sending student data to the frontend or exporting
    def to_dict(self):
        return {
            'id': self.id,  # Student's database ID
            'roll_no': self.roll_no,  # Student's roll number
            'name': self.name,  # Student's name
            'email': self.email,  # Student's email
            'courses': self.courses,  # List of enrolled courses
            'grades': [float(grade) for grade in self.grades],  # Convert all grades to float
            'created_at': self.created_at.isoformat() if self.created_at else None  # Convert datetime to ISO string
        }
    
    # Calculate and return the average grade for this student
    # Used in reports and student performance analysis
    def get_average_grade(self):
        # Check if student has any grades recorded
        if self.grades:
            # Calculate average: sum all grades and divide by count, round to 2 decimal places
            return round(sum(float(grade) for grade in self.grades) / len(self.grades), 2)
        # Return 0.0 if no grades exist
        return 0.0
