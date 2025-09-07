"""
Student Manager class that handles all student operations using custom data structures
"""

import json
import os
from core.data_structures import LinkedList, Stack, StudentDataProcessor

class StudentManager:
    """Manages student records using custom linked list and stack data structures"""
    
    def __init__(self, data_file='student_data.json'):
        self.students = LinkedList()
        self.operation_history = Stack(100)
        self.processor = StudentDataProcessor()
        self.data_file = data_file
        self.load_data()
    
    def add_student(self, student_data):
        """Add a new student to the system"""
        # Check if roll number already exists
        if self.students.find(student_data['roll_no']):
            return False
        
        # Log operation for undo functionality
        self.operation_history.push({
            'action': 'add',
            'data': student_data.copy(),
            'timestamp': self._get_timestamp()
        })
        
        # Add to linked list
        self.students.append(student_data)
        
        # Log operation in processor
        self.processor.log_operation('add_student', student_data)
        
        # Save to file
        self.save_data()
        
        return True
    
    def get_student(self, roll_no):
        """Get a student by roll number"""
        return self.students.find(roll_no)
    
    def get_all_students(self):
        """Get all students as a list"""
        return self.students.to_list()
    
    def update_student(self, roll_no, new_data):
        """Update a student's information"""
        # Get old data for undo functionality
        old_data = self.students.find(roll_no)
        if not old_data:
            return False
        
        # Log operation
        self.operation_history.push({
            'action': 'update',
            'roll_no': roll_no,
            'old_data': old_data.copy(),
            'new_data': new_data.copy(),
            'timestamp': self._get_timestamp()
        })
        
        # Update in linked list
        success = self.students.update(roll_no, new_data)
        
        if success:
            self.processor.log_operation('update_student', {
                'roll_no': roll_no,
                'old_data': old_data,
                'new_data': new_data
            })
            self.save_data()
        
        return success
    
    def delete_student(self, roll_no):
        """Delete a student from the system"""
        # Get student data for undo functionality
        student_data = self.students.find(roll_no)
        if not student_data:
            return False
        
        # Log operation
        self.operation_history.push({
            'action': 'delete',
            'data': student_data.copy(),
            'timestamp': self._get_timestamp()
        })
        
        # Delete from linked list
        success = self.students.delete(roll_no)
        
        if success:
            self.processor.log_operation('delete_student', student_data)
            self.save_data()
        
        return success
    
    def search_students(self, search_term):
        """Search students by name, email, or roll number"""
        return self.students.search(search_term)
    
    def filter_by_course(self, course_name):
        """Get all students enrolled in a specific course"""
        return self.students.filter_by_course(course_name)
    
    def filter_by_grade_range(self, min_grade, max_grade):
        """Get students within a specific grade range"""
        return self.students.filter_by_grade_range(min_grade, max_grade)
    
    def get_top_performers(self, limit=10):
        """Get top performing students"""
        all_students = self.get_all_students()
        
        # Calculate average grades and sort
        students_with_avg = []
        for student in all_students:
            grades = student.get('grades', [])
            if grades:
                avg_grade = sum(grades) / len(grades)
                student_copy = student.copy()
                student_copy['avg_grade'] = round(avg_grade, 2)
                students_with_avg.append(student_copy)
        
        # Sort by average grade (descending)
        students_with_avg.sort(key=lambda x: x['avg_grade'], reverse=True)
        
        return students_with_avg[:limit]
    
    def calculate_average_grade(self):
        """Calculate overall average grade across all students"""
        all_students = self.get_all_students()
        all_grades = []
        
        for student in all_students:
            grades = student.get('grades', [])
            all_grades.extend(grades)
        
        if not all_grades:
            return 0
        
        return round(sum(all_grades) / len(all_grades), 2)
    
    def get_course_statistics(self):
        """Get statistics for each course"""
        all_students = self.get_all_students()
        course_stats = {}
        
        for student in all_students:
            courses = student.get('courses', [])
            grades = student.get('grades', [])
            
            for course, grade in zip(courses, grades):
                if course not in course_stats:
                    course_stats[course] = {
                        'students': [],
                        'grades': [],
                        'total_students': 0,
                        'avg_grade': 0
                    }
                
                course_stats[course]['students'].append(student['name'])
                course_stats[course]['grades'].append(grade)
                course_stats[course]['total_students'] += 1
        
        # Calculate averages
        for course in course_stats:
            grades = course_stats[course]['grades']
            course_stats[course]['avg_grade'] = round(sum(grades) / len(grades), 2)
        
        return course_stats
    
    def get_operation_history(self, limit=10):
        """Get recent operation history"""
        history = []
        temp_stack = Stack()
        
        # Get items from stack (they come in reverse order)
        count = 0
        while not self.operation_history.is_empty() and count < limit:
            operation = self.operation_history.pop()
            history.append(operation)
            temp_stack.push(operation)
            count += 1
        
        # Restore the original stack
        while not temp_stack.is_empty():
            self.operation_history.push(temp_stack.pop())
        
        return history
    
    def undo_last_operation(self):
        """Undo the last operation (basic implementation)"""
        if self.operation_history.is_empty():
            return False, "No operations to undo"
        
        last_operation = self.operation_history.pop()
        action = last_operation.get('action')
        
        try:
            if action == 'add':
                # Undo add by deleting the student
                roll_no = last_operation['data']['roll_no']
                self.students.delete(roll_no)
                
            elif action == 'delete':
                # Undo delete by adding the student back
                self.students.append(last_operation['data'])
                
            elif action == 'update':
                # Undo update by restoring old data
                roll_no = last_operation['roll_no']
                old_data = last_operation['old_data']
                self.students.update(roll_no, old_data)
            
            self.save_data()
            return True, f"Successfully undid {action} operation"
            
        except Exception as e:
            # Push operation back to stack if undo fails
            self.operation_history.push(last_operation)
            return False, f"Failed to undo operation: {str(e)}"
    
    def save_data(self):
        """Save student data to JSON file"""
        try:
            students_list = self.get_all_students()
            with open(self.data_file, 'w') as f:
                json.dump(students_list, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load student data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    students_list = json.load(f)
                    for student in students_list:
                        self.students.append(student)
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def get_statistics(self):
        """Get comprehensive statistics using the processor"""
        all_students = self.get_all_students()
        return self.processor.calculate_statistics(all_students)
    
    def export_to_json(self):
        """Export all student data to JSON format"""
        return json.dumps(self.get_all_students(), indent=2)
    
    def import_from_json(self, json_data):
        """Import student data from JSON format"""
        try:
            students_list = json.loads(json_data)
            imported_count = 0
            
            for student_data in students_list:
                if self.add_student(student_data):
                    imported_count += 1
            
            return imported_count, len(students_list)
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        except Exception as e:
            raise ValueError(f"Import error: {str(e)}")
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
