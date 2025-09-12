"""
Abstract repository interface for student data operations.
Supports both SQLAlchemy and direct psycopg2 implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class StudentRepository(ABC):
    """Abstract interface for student data operations"""
    
    @abstractmethod
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students as dictionaries"""
        pass
    
    @abstractmethod
    def get_student_by_roll(self, roll_no: str) -> Optional[Dict[str, Any]]:
        """Get student by roll number"""
        pass
    
    @abstractmethod
    def add_student(self, roll_no: str, name: str, email: str, courses: List[str], grades: List[float]) -> bool:
        """Add a new student"""
        pass
    
    @abstractmethod
    def update_student(self, roll_no: str, name: str, email: str, courses: List[str], grades: List[float]) -> bool:
        """Update an existing student"""
        pass
    
    @abstractmethod
    def delete_student(self, roll_no: str) -> bool:
        """Delete a student by roll number"""
        pass
    
    @abstractmethod
    def search_students(self, search_term: str) -> List[Dict[str, Any]]:
        """Search students by name, roll number, or email"""
        pass
    
    @abstractmethod
    def execute_select_query(self, query: str) -> List[List[Any]]:
        """Execute a SELECT query and return results"""
        pass
    
    @abstractmethod
    def get_total_count(self) -> int:
        """Get total number of students"""
        pass
    
    @abstractmethod
    def initialize_database(self) -> bool:
        """Initialize database tables if needed"""
        pass