from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    
    # Use JSON columns for compatibility between PostgreSQL and SQLite
    _courses = db.Column('courses', db.Text, nullable=False)
    _grades = db.Column('grades', db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def courses(self):
        """Get courses as a list"""
        return json.loads(self._courses) if self._courses else []
    
    @courses.setter
    def courses(self, value):
        """Set courses from a list"""
        self._courses = json.dumps(value if value else [])
    
    @property
    def grades(self):
        """Get grades as a list of floats"""
        grades_data = json.loads(self._grades) if self._grades else []
        return [float(grade) for grade in grades_data]
    
    @grades.setter
    def grades(self, value):
        """Set grades from a list"""
        self._grades = json.dumps([float(grade) for grade in value] if value else [])
    
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