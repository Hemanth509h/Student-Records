"""
SQLAlchemy implementation of StudentRepository.
Uses the existing SQLAlchemy ORM models.
"""

from typing import List, Dict, Any, Optional
from student_repository import StudentRepository
from models import Student, db
from sqlalchemy import text


class SQLAlchemyStudentRepository(StudentRepository):
    """SQLAlchemy implementation of student repository"""
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students as dictionaries"""
        students = Student.query.all()
        return [self._student_to_dict(student) for student in students]
    
    def get_student_by_roll(self, roll_no: str) -> Optional[Dict[str, Any]]:
        """Get student by roll number"""
        student = Student.query.filter_by(roll_no=roll_no).first()
        return self._student_to_dict(student) if student else None
    
    def add_student(self, roll_no: str, name: str, email: str, courses: List[str], grades: List[float]) -> bool:
        """Add a new student"""
        try:
            # Check if student already exists
            if Student.query.filter_by(roll_no=roll_no).first():
                return False
                
            student = Student()
            student.roll_no = roll_no
            student.name = name
            student.email = email
            student.courses = courses
            student.grades = grades
            db.session.add(student)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def update_student(self, roll_no: str, name: str, email: str, courses: List[str], grades: List[float]) -> bool:
        """Update an existing student"""
        try:
            student = Student.query.filter_by(roll_no=roll_no).first()
            if not student:
                return False
                
            student.name = name
            student.email = email
            student.courses = courses
            student.grades = grades
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def delete_student(self, roll_no: str) -> bool:
        """Delete a student by roll number"""
        try:
            student = Student.query.filter_by(roll_no=roll_no).first()
            if not student:
                return False
                
            db.session.delete(student)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def search_students(self, search_term: str) -> List[Dict[str, Any]]:
        """Search students by name, roll number, or email"""
        students = Student.query.filter(
            db.or_(
                Student.name.ilike(f'%{search_term}%'),
                Student.roll_no.ilike(f'%{search_term}%'),
                Student.email.ilike(f'%{search_term}%')
            )
        ).all()
        return [self._student_to_dict(student) for student in students]
    
    def execute_select_query(self, query: str) -> List[List[Any]]:
        """Execute a SELECT query and return results"""
        result = db.session.execute(text(query))
        return [list(row) for row in result.fetchall()]
    
    def get_total_count(self) -> int:
        """Get total number of students"""
        return Student.query.count()
    
    def initialize_database(self) -> bool:
        """Initialize database tables if needed"""
        try:
            db.create_all()
            return True
        except Exception:
            return False
    
    def _student_to_dict(self, student: Student) -> Dict[str, Any]:
        """Convert Student ORM object to dictionary"""
        return {
            'id': student.id,
            'roll_no': student.roll_no,
            'name': student.name,
            'email': student.email,
            'courses': student.courses or [],
            'grades': student.grades or [],
            'created_at': student.created_at
        }