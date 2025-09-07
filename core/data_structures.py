"""
Custom data structures for student record processing
Implements Linked List and Stack for efficient data manipulation
"""
from typing import Optional, Any

class Node:
    """Node class for linked list implementation"""
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional['Node'] = None

class LinkedList:
    """Custom Linked List implementation for student records"""
    
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, data):
        """Add a new node at the end of the list"""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
    
    def prepend(self, data):
        """Add a new node at the beginning of the list"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
    
    def delete(self, roll_no):
        """Delete a student by roll number"""
        if not self.head:
            return False
        
        # If head node contains the roll_no
        if self.head.data.get('roll_no') == roll_no:
            self.head = self.head.next
            self.size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.data.get('roll_no') == roll_no:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        
        return False
    
    def find(self, roll_no):
        """Find a student by roll number"""
        current = self.head
        while current:
            if current.data.get('roll_no') == roll_no:
                return current.data
            current = current.next
        return None
    
    def search(self, search_term):
        """Search students by name, email, or roll number"""
        results = []
        current = self.head
        search_term = search_term.lower()
        
        while current:
            student = current.data
            if (search_term in student.get('name', '').lower() or
                search_term in student.get('email', '').lower() or
                search_term in student.get('roll_no', '').lower()):
                results.append(student)
            current = current.next
        
        return results
    
    def update(self, roll_no, new_data):
        """Update a student's data"""
        current = self.head
        while current:
            if current.data.get('roll_no') == roll_no:
                current.data = new_data
                return True
            current = current.next
        return False
    
    def to_list(self):
        """Convert linked list to Python list"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def filter_by_course(self, course_name):
        """Filter students by course name"""
        results = []
        current = self.head
        
        while current:
            student = current.data
            courses = student.get('courses', [])
            if course_name in courses:
                results.append(student)
            current = current.next
        
        return results
    
    def filter_by_grade_range(self, min_grade, max_grade):
        """Filter students by grade range"""
        results = []
        current = self.head
        
        while current:
            student = current.data
            grades = student.get('grades', [])
            if grades:
                avg_grade = sum(grades) / len(grades)
                if min_grade <= avg_grade <= max_grade:
                    results.append(student)
            current = current.next
        
        return results
    
    def get_length(self):
        """Get the length of the linked list"""
        return self.size
    
    def is_empty(self):
        """Check if the linked list is empty"""
        return self.head is None

class Stack:
    """Custom Stack implementation for operation history and undo functionality"""
    
    def __init__(self, max_size=100):
        self.items = []
        self.max_size = max_size
    
    def push(self, item):
        """Add an item to the top of the stack"""
        if len(self.items) >= self.max_size:
            # Remove oldest item if stack is at max capacity
            self.items.pop(0)
        self.items.append(item)
    
    def pop(self):
        """Remove and return the top item from the stack"""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self):
        """Return the top item without removing it"""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self):
        """Check if the stack is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Return the size of the stack"""
        return len(self.items)
    
    def clear(self):
        """Clear all items from the stack"""
        self.items = []
    
    def to_list(self):
        """Convert stack to list (top to bottom)"""
        return list(reversed(self.items))

class Queue:
    """Custom Queue implementation for batch processing"""
    
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        """Add an item to the rear of the queue"""
        self.items.append(item)
    
    def dequeue(self):
        """Remove and return the front item from the queue"""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def front(self):
        """Return the front item without removing it"""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.items) == 0
    
    def size(self):
        """Return the size of the queue"""
        return len(self.items)
    
    def clear(self):
        """Clear all items from the queue"""
        self.items = []

class StudentDataProcessor:
    """Utility class for processing student data using custom data structures"""
    
    def __init__(self):
        self.operation_history = Stack(50)  # Keep last 50 operations
        self.batch_queue = Queue()
    
    def log_operation(self, operation_type, data):
        """Log an operation to the history stack"""
        operation = {
            'type': operation_type,
            'data': data,
            'timestamp': self._get_timestamp()
        }
        self.operation_history.push(operation)
    
    def get_operation_history(self, limit=10):
        """Get recent operation history"""
        history = self.operation_history.to_list()
        return history[:limit]
    
    def sort_students_by_grade(self, students):
        """Sort students by average grade using custom comparison"""
        def get_average_grade(student):
            grades = student.get('grades', [])
            return sum(grades) / len(grades) if grades else 0
        
        # Simple bubble sort implementation for educational purposes
        student_list = students.copy()
        n = len(student_list)
        
        for i in range(n):
            for j in range(0, n - i - 1):
                if get_average_grade(student_list[j]) < get_average_grade(student_list[j + 1]):
                    student_list[j], student_list[j + 1] = student_list[j + 1], student_list[j]
        
        return student_list
    
    def group_by_course(self, students):
        """Group students by courses they are enrolled in"""
        course_groups = {}
        
        for student in students:
            courses = student.get('courses', [])
            for course in courses:
                if course not in course_groups:
                    course_groups[course] = []
                course_groups[course].append(student)
        
        return course_groups
    
    def calculate_statistics(self, students):
        """Calculate various statistics for student data"""
        if not students:
            return {}
        
        total_students = len(students)
        all_grades = []
        course_count = {}
        
        for student in students:
            grades = student.get('grades', [])
            all_grades.extend(grades)
            
            courses = student.get('courses', [])
            for course in courses:
                course_count[course] = course_count.get(course, 0) + 1
        
        if not all_grades:
            return {'total_students': total_students}
        
        # Calculate statistics
        avg_grade = sum(all_grades) / len(all_grades)
        min_grade = min(all_grades)
        max_grade = max(all_grades)
        
        # Find median
        sorted_grades = sorted(all_grades)
        n = len(sorted_grades)
        median_grade = (sorted_grades[n//2] + sorted_grades[(n-1)//2]) / 2
        
        return {
            'total_students': total_students,
            'total_grades': len(all_grades),
            'average_grade': round(avg_grade, 2),
            'median_grade': round(median_grade, 2),
            'min_grade': min_grade,
            'max_grade': max_grade,
            'most_popular_course': max(course_count.keys(), key=lambda k: course_count[k]) if course_count else None,
            'course_distribution': course_count
        }
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
