"""
Direct psycopg2 implementation of StudentRepository.
Uses raw SQL queries with connection pooling.
"""

import os
import psycopg2
import psycopg2.pool
from typing import List, Dict, Any, Optional
from student_repository import StudentRepository
from contextlib import contextmanager


class Psycopg2StudentRepository(StudentRepository):
    """Direct psycopg2 implementation of student repository"""
    
    def __init__(self):
        """Initialize connection pool"""
        self.connection_pool = None
        self._initialize_pool()
        if not self.connection_pool:
            raise Exception("Failed to initialize connection pool")
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/student_management')
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=database_url
            )
        except Exception as e:
            print(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = None
        try:
            if self.connection_pool:
                conn = self.connection_pool.getconn()
            else:
                raise Exception("Connection pool not initialized")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn and self.connection_pool:
                self.connection_pool.putconn(conn)
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students as dictionaries"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, roll_no, name, email, courses, grades, created_at 
                    FROM students ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
            finally:
                if cursor:
                    cursor.close()
    
    def get_student_by_roll(self, roll_no: str) -> Optional[Dict[str, Any]]:
        """Get student by roll number"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, roll_no, name, email, courses, grades, created_at 
                    FROM students WHERE roll_no = %s
                """, (roll_no,))
                row = cursor.fetchone()
                return self._row_to_dict(row) if row else None
            finally:
                if cursor:
                    cursor.close()
    
    def add_student(self, roll_no: str, name: str, email: str, courses: List[str], grades: List[float]) -> bool:
        """Add a new student"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO students (roll_no, name, email, courses, grades)
                    VALUES (%s, %s, %s, %s, %s)
                """, (roll_no, name, email, courses, grades))
                conn.commit()
                return True
            except psycopg2.IntegrityError:
                # Duplicate roll number - rollback handled by context manager
                conn.rollback()
                return False
            except Exception:
                # Other errors - rollback handled by context manager
                conn.rollback()
                return False
            finally:
                if cursor:
                    cursor.close()
    
    def update_student(self, roll_no: str, name: str, email: str, courses: List[str], grades: List[float]) -> bool:
        """Update an existing student"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE students 
                    SET name = %s, email = %s, courses = %s, grades = %s
                    WHERE roll_no = %s
                """, (name, email, courses, grades, roll_no))
                
                success = cursor.rowcount > 0
                conn.commit()
                return success
            except Exception:
                # Rollback on any error
                conn.rollback()
                return False
            finally:
                if cursor:
                    cursor.close()
    
    def delete_student(self, roll_no: str) -> bool:
        """Delete a student by roll number"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
                success = cursor.rowcount > 0
                conn.commit()
                return success
            except Exception:
                # Rollback on any error
                conn.rollback()
                return False
            finally:
                if cursor:
                    cursor.close()
    
    def search_students(self, search_term: str) -> List[Dict[str, Any]]:
        """Search students by name, roll number, or email"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                search_pattern = f'%{search_term}%'
                cursor.execute("""
                    SELECT id, roll_no, name, email, courses, grades, created_at 
                    FROM students 
                    WHERE name ILIKE %s OR roll_no ILIKE %s OR email ILIKE %s
                    ORDER BY created_at DESC
                """, (search_pattern, search_pattern, search_pattern))
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
            finally:
                if cursor:
                    cursor.close()
    
    def execute_select_query(self, query: str) -> List[List[Any]]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchmany(100)  # Limit to 100 rows for safety
                return [list(row) for row in rows]
            finally:
                if cursor:
                    cursor.close()
    
    def get_total_count(self) -> int:
        """Get total number of students"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM students")
                count = cursor.fetchone()[0]
                return count
            finally:
                if cursor:
                    cursor.close()
    
    def initialize_database(self) -> bool:
        """Initialize database tables if needed"""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id SERIAL PRIMARY KEY,
                        roll_no VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        courses TEXT[],
                        grades NUMERIC[],
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                conn.commit()
                return True
            except Exception as e:
                print(f"Failed to initialize database: {e}")
                conn.rollback()
                return False
            finally:
                if cursor:
                    cursor.close()
    
    def close_pool(self):
        """Close the connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'roll_no': row[1],
            'name': row[2],
            'email': row[3],
            'courses': row[4] or [],
            'grades': row[5] or [],
            'created_at': row[6]
        }