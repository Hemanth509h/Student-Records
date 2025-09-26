from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, date
from flask_login import UserMixin
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
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
    profile_photo = db.Column(db.String(255), nullable=True)  # Filename of profile photo
    phone = db.Column(db.String(20), nullable=True)  # Additional contact info
    address = db.Column(db.Text, nullable=True)  # Student address
    date_of_birth = db.Column(db.Date, nullable=True)  # Student's date of birth
    gender = db.Column(db.String(10), nullable=True)  # Student gender
    guardian_name = db.Column(db.String(100), nullable=True)  # Guardian/parent name
    guardian_phone = db.Column(db.String(20), nullable=True)  # Guardian contact
    courses = db.Column(ARRAY(db.String), nullable=False)
    grades = db.Column(ARRAY(db.Numeric), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Student {self.roll_no}: {self.name}>'
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'id': self.id,
            'roll_no': self.roll_no,
            'name': self.name,
            'email': self.email,
            'profile_photo': self.profile_photo,
            'phone': self.phone,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'guardian_name': self.guardian_name,
            'guardian_phone': self.guardian_phone,
            'courses': self.courses,
            'grades': [float(grade) for grade in self.grades],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_profile_photo_url(self):
        """Get the URL for the profile photo"""
        if self.profile_photo:
            return f'/static/uploads/profiles/{self.profile_photo}'
        return '/static/images/default-avatar.png'  # We'll create this
    
    def get_average_grade(self):
        """Calculate average grade for this student"""
        if self.grades:
            return round(sum(float(grade) for grade in self.grades) / len(self.grades), 2)
        return 0.0