# Student Record Management System - Mind Map & Code Explanation

## 🗺️ **PROJECT MIND MAP**

```
Student Record Management System
├── 🌐 Web Layer (Flask)
│   ├── app.py (Main Flask Application)
│   │   ├── Route Handlers (/,/add_student,/edit_student,/delete_student,/query,/reports,/search,/export)
│   │   ├── Form Processing & Validation
│   │   ├── Session Management
│   │   └── Error Handling & Flash Messages
│   └── main.py (Application Entry Point)
│
├── 🗂️ Data Layer (Custom Data Structures)
│   └── data_structures.py
│       ├── Node Class (LinkedList building block)
│       ├── LinkedList Class (Student storage & operations)
│       ├── Stack Class (Operation history & undo)
│       ├── Queue Class (Batch processing)
│       └── StudentDataProcessor (Utility operations)
│
├── 🎯 Business Logic Layer
│   ├── student_manager.py (Core Student Operations)
│   │   ├── CRUD Operations (Create, Read, Update, Delete)
│   │   ├── Data Persistence (JSON file I/O)
│   │   ├── Search & Filter Operations
│   │   ├── Statistics & Analytics
│   │   └── Operation History & Undo
│   └── query_engine.py (SQL-like Query Processing)
│       ├── Query Parser (SELECT, WHERE, ORDER BY, etc.)
│       ├── Condition Evaluation
│       ├── Data Filtering & Sorting
│       └── Result Formatting
│
├── 🎨 Presentation Layer (Frontend)
│   ├── templates/ (Jinja2 HTML Templates)
│   │   ├── base.html (Base template with dark theme)
│   │   ├── index.html (Dashboard with statistics)
│   │   ├── add_student.html (Student creation form)
│   │   ├── edit_student.html (Student modification form)
│   │   ├── query.html (SQL-like query interface)
│   │   └── reports.html (Analytics & charts)
│   └── static/ (Static Assets)
│       ├── css/style.css (Dark theme styling)
│       └── js/main.js (Interactive functionality)
│
└── 📊 Data Flow
    ├── User Input → Flask Routes → Business Logic → Data Structures → JSON Storage
    ├── Query Processing → LinkedList Traversal → Filtered Results → HTML Display
    └── Statistics → Data Aggregation → Chart Rendering → Dashboard
```

---

## 📁 **FILE-BY-FILE CODE EXPLANATION**

### 🚀 **1. main.py** (Application Entry Point)

```python
# Line 1: Import the Flask application instance from app.py
from app import app

# Line 3-4: Main execution guard - only run server if script is executed directly
if __name__ == '__main__':
    # Start Flask development server on all interfaces (0.0.0.0) port 5000 with debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Purpose:** Simple entry point that starts the Flask web server
**Key Concepts:** 
- `host='0.0.0.0'` allows external connections (required for Replit)
- `debug=True` enables auto-reload and detailed error messages
- `if __name__ == '__main__'` prevents server start when imported as module

---

### 🌐 **2. app.py** (Main Flask Application - 278 lines)

```python
# Lines 1-6: Import all required modules
import os                    # For environment variable access
import logging              # For debugging and error tracking
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# Flask core functions for web framework functionality
from student_manager import StudentManager    # Custom student management logic
from query_engine import QueryEngine         # Custom SQL-like query processor
import json                                  # For JSON data handling

# Lines 8-9: Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)    # Set log level to DEBUG for detailed output

# Lines 11-13: Create and configure Flask application
app = Flask(__name__)                        # Create Flask app instance
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
# Set secret key for session security (from environment or default)

# Lines 15-17: Initialize custom managers
student_manager = StudentManager()          # Create student management instance
query_engine = QueryEngine(student_manager) # Create query engine with student manager reference

# Lines 19-28: Dashboard route (homepage)
@app.route('/')                             # Route decorator for root URL
def index():                                # Function name becomes endpoint name
    """Main dashboard showing all students"""
    students = student_manager.get_all_students()  # Retrieve all student records
    stats = {                               # Calculate dashboard statistics
        'total_students': len(students),    # Count total students
        'total_courses': len(set(course for student in students for course in student.get('courses', []))),
        # Count unique courses across all students using set comprehension
        'avg_grade': student_manager.calculate_average_grade()  # Calculate overall average
    }
    return render_template('index.html', students=students, stats=stats)
    # Render dashboard template with data

# Lines 30-78: Add student route (GET and POST)
@app.route('/add_student', methods=['GET', 'POST'])  # Handle both form display and submission
def add_student():
    """Add a new student"""
    if request.method == 'POST':            # If form was submitted
        try:                                # Error handling wrapper
            # Lines 35-39: Extract form data with whitespace removal
            roll_no = request.form['roll_no'].strip()
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            courses_str = request.form['courses'].strip()
            grades_str = request.form['grades'].strip()
            
            # Lines 41-44: Validate all required fields are present
            if not all([roll_no, name, email, courses_str, grades_str]):
                flash('All fields are required', 'error')    # Show error message
                return render_template('add_student.html')   # Return to form
            
            # Lines 46-47: Parse comma-separated courses
            courses = [course.strip() for course in courses_str.split(',')]
            
            # Lines 48-52: Parse and validate grades as numbers
            try:
                grades = [float(grade.strip()) for grade in grades_str.split(',')]
            except ValueError:              # Handle invalid number format
                flash('Grades must be valid numbers', 'error')
                return render_template('add_student.html')
            
            # Lines 54-56: Validate courses and grades count match
            if len(courses) != len(grades):
                flash('Number of courses must match number of grades', 'error')
                return render_template('add_student.html')
            
            # Lines 58-65: Create student data dictionary
            student_data = {
                'roll_no': roll_no,
                'name': name,
                'email': email,
                'courses': courses,
                'grades': grades
            }
            
            # Lines 67-72: Attempt to add student and handle result
            success = student_manager.add_student(student_data)
            if success:
                flash(f'Student {name} added successfully!', 'success')
                return redirect(url_for('index'))  # Redirect to dashboard
            else:
                flash('Roll number already exists', 'error')
                
        # Lines 74-76: Global error handling
        except Exception as e:
            logging.error(f"Error adding student: {e}")    # Log error details
            flash('An error occurred while adding the student', 'error')
    
    return render_template('add_student.html')  # Show form (GET request or error)

# Lines 80-129: Edit student route
@app.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
def edit_student(roll_no):                  # roll_no from URL parameter
    """Edit an existing student"""
    student = student_manager.get_student(roll_no)  # Retrieve student by roll number
    if not student:                         # Check if student exists
        flash('Student not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':            # Handle form submission
        try:
            # Lines 90-93: Extract updated form data
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            courses_str = request.form['courses'].strip()
            grades_str = request.form['grades'].strip()
            
            # Lines 95-98: Validate required fields
            if not all([name, email, courses_str, grades_str]):
                flash('All fields are required', 'error')
                return render_template('edit_student.html', student=student)
            
            # Lines 100-110: Parse and validate courses and grades (same logic as add)
            courses = [course.strip() for course in courses_str.split(',')]
            try:
                grades = [float(grade.strip()) for grade in grades_str.split(',')]
            except ValueError:
                flash('Grades must be valid numbers', 'error')
                return render_template('edit_student.html', student=student)
            
            if len(courses) != len(grades):
                flash('Number of courses must match number of grades', 'error')
                return render_template('edit_student.html', student=student)
            
            # Lines 112-119: Create updated student data
            updated_data = {
                'roll_no': roll_no,        # Keep original roll number
                'name': name,
                'email': email,
                'courses': courses,
                'grades': grades
            }
            
            # Lines 121-123: Update student and redirect
            student_manager.update_student(roll_no, updated_data)
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('index'))
            
        # Lines 125-127: Error handling
        except Exception as e:
            logging.error(f"Error updating student: {e}")
            flash('An error occurred while updating the student', 'error')
    
    return render_template('edit_student.html', student=student)  # Show edit form

# Lines 131-140: Delete student route
@app.route('/delete_student/<roll_no>')     # Simple GET route for deletion
def delete_student(roll_no):
    """Delete a student"""
    student = student_manager.get_student(roll_no)  # Get student for confirmation message
    if student:
        student_manager.delete_student(roll_no)      # Perform deletion
        flash(f'Student {student["name"]} deleted successfully!', 'success')
    else:
        flash('Student not found', 'error')
    return redirect(url_for('index'))        # Always redirect to dashboard

# Lines 142-158: Query interface route
@app.route('/query', methods=['GET', 'POST'])
def query():
    """SQL-like query interface"""
    results = []                            # Initialize empty results
    query_text = ""                        # Initialize empty query
    
    if request.method == 'POST':           # Handle query submission
        query_text = request.form['query'].strip()  # Get query from form
        if query_text:                     # If query is not empty
            try:
                results = query_engine.execute_query(query_text)  # Execute query
                flash(f'Query executed successfully. Found {len(results)} results.', 'success')
            except Exception as e:         # Handle query errors
                flash(f'Query error: {str(e)}', 'error')
                results = []               # Reset results on error
    
    return render_template('query.html', results=results, query_text=query_text)

# Lines 160-236: Reports and analytics route
@app.route('/reports')
def reports():
    """Generate reports and statistics"""
    try:
        all_students = student_manager.get_all_students()  # Get all student data
        total_students = len(all_students)                 # Count students
        
        # Lines 170-172: Initialize statistics containers
        course_stats = {}                  # Dictionary for course statistics
        grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}  # Grade counters
        
        # Lines 174-195: Process each student for statistics
        for student in all_students:
            courses = student.get('courses', [])
            grades = student.get('grades', [])
            
            # Lines 178-183: Calculate course statistics
            for course, grade in zip(courses, grades):  # Pair courses with grades
                if course not in course_stats:
                    course_stats[course] = {'total_students': 0, 'total_grade': 0, 'avg_grade': 0}
                
                course_stats[course]['total_students'] += 1
                course_stats[course]['total_grade'] += grade
                
                # Lines 185-195: Categorize grades for distribution
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
        
        # Lines 197-202: Calculate average grades for each course
        for course in course_stats:
            if course_stats[course]['total_students'] > 0:
                course_stats[course]['avg_grade'] = round(
                    course_stats[course]['total_grade'] / course_stats[course]['total_students'], 2
                )
        
        # Lines 204-205: Get top performers
        top_performers = student_manager.get_top_performers(5)
        
        # Lines 207-219: Find students needing attention (average < 70)
        low_performers = []
        for student in all_students:
            grades = student.get('grades', [])
            if grades:
                avg_grade = sum(grades) / len(grades)
                if avg_grade < 70:
                    student_copy = student.copy()
                    student_copy['avg_grade'] = round(avg_grade, 2)
                    low_performers.append(student_copy)
        
        low_performers.sort(key=lambda x: x['avg_grade'])  # Sort by grade ascending
        
        # Lines 221-229: Compile report data
        report_data = {
            'total_students': total_students,
            'total_courses': len(course_stats),
            'overall_avg': student_manager.calculate_average_grade(),
            'course_stats': course_stats,
            'grade_distribution': grade_distribution,
            'top_performers': top_performers,
            'low_performers': low_performers[:10]  # Limit to top 10
        }
        
        return render_template('reports.html', report_data=report_data)
        
    # Lines 233-236: Error handling for reports
    except Exception as e:
        logging.error(f"Error generating reports: {e}")
        flash('An error occurred while generating reports', 'error')
        return redirect(url_for('index'))

# Lines 238-248: Search functionality
@app.route('/search')
def search():
    """Search students"""
    search_term = request.args.get('search', '').strip()  # Get search term from URL parameter
    students = []                          # Initialize empty results
    
    if search_term:                        # If search term provided
        students = student_manager.search_students(search_term)  # Perform search
        flash(f'Found {len(students)} students matching "{search_term}"', 'info')
    
    return render_template('index.html', students=students, search_term=search_term)

# Lines 250-274: Data export functionality
@app.route('/export')
def export_data():
    """Export student data as JSON"""
    try:
        students = student_manager.get_all_students()  # Get all student data
        
        # Lines 255-258: Import Response for file download
        from flask import Response
        import json
        
        json_data = json.dumps(students, indent=2)     # Convert to formatted JSON
        
        # Lines 261-266: Create downloadable response
        response = Response(
            json_data,
            mimetype='application/json',               # Set content type
            headers={'Content-Disposition': 'attachment; filename=student_records.json'}
        )                                             # Force download with filename
        
        flash('Student data exported successfully!', 'success')
        return response
        
    # Lines 270-274: Error handling for export
    except Exception as e:
        logging.error(f"Error exporting data: {e}")
        flash('An error occurred while exporting data', 'error')
        return redirect(url_for('index'))

# Lines 276-277: Development server configuration
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Start development server
```

---

### 🗂️ **3. data_structures.py** (Custom Data Structures - 313 lines)

```python
# Lines 1-4: Module documentation
"""
Custom data structures for student record processing
Implements Linked List and Stack for efficient data manipulation
"""

# Lines 6-10: Node class definition
class Node:
    """Node class for linked list implementation"""
    def __init__(self, data):              # Constructor takes data parameter
        self.data = data                   # Store the actual data
        self.next = None                   # Initialize next pointer to None

# Lines 12-140: LinkedList class implementation
class LinkedList:
    """Custom Linked List implementation for student records"""
    
    def __init__(self):                    # Constructor
        self.head = None                   # Initialize head pointer to None
        self.size = 0                      # Track list size for efficiency
    
    # Lines 19-29: Append method (add to end)
    def append(self, data):
        """Add a new node at the end of the list"""
        new_node = Node(data)              # Create new node with data
        if not self.head:                  # If list is empty
            self.head = new_node           # New node becomes head
        else:
            current = self.head            # Start from head
            while current.next:            # Traverse to last node
                current = current.next
            current.next = new_node        # Link last node to new node
        self.size += 1                     # Increment size counter
    
    # Lines 31-36: Prepend method (add to beginning)
    def prepend(self, data):
        """Add a new node at the beginning of the list"""
        new_node = Node(data)              # Create new node
        new_node.next = self.head          # Point new node to current head
        self.head = new_node               # New node becomes head
        self.size += 1                     # Increment size
    
    # Lines 38-57: Delete method (remove by roll number)
    def delete(self, roll_no):
        """Delete a student by roll number"""
        if not self.head:                  # If list is empty
            return False                   # Nothing to delete
        
        # Lines 44-47: Handle deletion of head node
        if self.head.data.get('roll_no') == roll_no:
            self.head = self.head.next     # Move head to next node
            self.size -= 1                 # Decrement size
            return True                    # Deletion successful
        
        # Lines 49-56: Handle deletion of non-head nodes
        current = self.head
        while current.next:                # Traverse until second-to-last node
            if current.next.data.get('roll_no') == roll_no:  # Found target
                current.next = current.next.next  # Skip target node
                self.size -= 1             # Decrement size
                return True                # Deletion successful
            current = current.next         # Move to next node
        
        return False                       # Roll number not found
    
    # Lines 59-66: Find method (search by roll number)
    def find(self, roll_no):
        """Find a student by roll number"""
        current = self.head                # Start from head
        while current:                     # Traverse entire list
            if current.data.get('roll_no') == roll_no:  # Check if match
                return current.data        # Return student data
            current = current.next         # Move to next node
        return None                        # Not found
    
    # Lines 68-82: Search method (flexible text search)
    def search(self, search_term):
        """Search students by name, email, or roll number"""
        results = []                       # Initialize results list
        current = self.head                # Start from head
        search_term = search_term.lower() # Convert to lowercase for case-insensitive search
        
        while current:                     # Traverse entire list
            student = current.data
            # Lines 76-78: Check multiple fields for search term
            if (search_term in student.get('name', '').lower() or
                search_term in student.get('email', '').lower() or
                search_term in student.get('roll_no', '').lower()):
                results.append(student)    # Add to results if match found
            current = current.next         # Move to next node
        
        return results                     # Return all matching students
    
    # Lines 84-92: Update method (modify existing student)
    def update(self, roll_no, new_data):
        """Update a student's data"""
        current = self.head                # Start from head
        while current:                     # Traverse list
            if current.data.get('roll_no') == roll_no:  # Find target student
                current.data = new_data    # Replace data
                return True                # Update successful
            current = current.next         # Move to next node
        return False                       # Student not found
    
    # Lines 94-101: Convert to Python list
    def to_list(self):
        """Convert linked list to Python list"""
        result = []                        # Initialize result list
        current = self.head                # Start from head
        while current:                     # Traverse entire list
            result.append(current.data)    # Add each student to result
            current = current.next         # Move to next node
        return result                      # Return Python list
    
    # Lines 103-115: Filter by course method
    def filter_by_course(self, course_name):
        """Filter students by course name"""
        results = []                       # Initialize results
        current = self.head                # Start traversal
        
        while current:                     # Traverse list
            student = current.data
            courses = student.get('courses', [])  # Get student's courses
            if course_name in courses:     # Check if enrolled in target course
                results.append(student)    # Add to results
            current = current.next         # Move to next node
        
        return results                     # Return filtered students
    
    # Lines 117-131: Filter by grade range method
    def filter_by_grade_range(self, min_grade, max_grade):
        """Filter students by grade range"""
        results = []                       # Initialize results
        current = self.head                # Start traversal
        
        while current:                     # Traverse list
            student = current.data
            grades = student.get('grades', [])  # Get student's grades
            if grades:                     # If student has grades
                avg_grade = sum(grades) / len(grades)  # Calculate average
                if min_grade <= avg_grade <= max_grade:  # Check if in range
                    results.append(student)  # Add to results
            current = current.next         # Move to next node
        
        return results                     # Return filtered students
    
    # Lines 133-135: Get length method
    def get_length(self):
        """Get the length of the linked list"""
        return self.size                   # Return stored size
    
    # Lines 137-139: Check if empty method
    def is_empty(self):
        """Check if the linked list is empty"""
        return self.head is None           # True if head is None

# Lines 141-181: Stack class implementation
class Stack:
    """Custom Stack implementation for operation history and undo functionality"""
    
    def __init__(self, max_size=100):      # Constructor with optional max size
        self.items = []                    # Use Python list as underlying storage
        self.max_size = max_size           # Set maximum capacity
    
    # Lines 148-153: Push method (add to top)
    def push(self, item):
        """Add an item to the top of the stack"""
        if len(self.items) >= self.max_size:  # Check if at capacity
            self.items.pop(0)              # Remove oldest item (bottom)
        self.items.append(item)            # Add new item to top
    
    # Lines 155-159: Pop method (remove from top)
    def pop(self):
        """Remove and return the top item from the stack"""
        if self.is_empty():                # Check if stack is empty
            return None                    # Return None if empty
        return self.items.pop()            # Remove and return top item
    
    # Lines 161-165: Peek method (view top without removing)
    def peek(self):
        """Return the top item without removing it"""
        if self.is_empty():                # Check if stack is empty
            return None                    # Return None if empty
        return self.items[-1]              # Return top item (last in list)
    
    # Lines 167-169: Check if empty method
    def is_empty(self):
        """Check if the stack is empty"""
        return len(self.items) == 0        # True if no items
    
    # Lines 171-173: Get size method
    def size(self):
        """Return the size of the stack"""
        return len(self.items)             # Return count of items
    
    # Lines 175-177: Clear method
    def clear(self):
        """Clear all items from the stack"""
        self.items = []                    # Reset to empty list
    
    # Lines 179-181: Convert to list method
    def to_list(self):
        """Convert stack to list (top to bottom)"""
        return list(reversed(self.items))  # Return reversed list (top first)

# Lines 183-216: Queue class implementation
class Queue:
    """Custom Queue implementation for batch processing"""
    
    def __init__(self):                    # Constructor
        self.items = []                    # Use Python list as storage
    
    # Lines 189-191: Enqueue method (add to rear)
    def enqueue(self, item):
        """Add an item to the rear of the queue"""
        self.items.append(item)            # Add to end of list
    
    # Lines 193-197: Dequeue method (remove from front)
    def dequeue(self):
        """Remove and return the front item from the queue"""
        if self.is_empty():                # Check if queue is empty
            return None                    # Return None if empty
        return self.items.pop(0)           # Remove and return first item
    
    # Lines 199-203: Front method (view front without removing)
    def front(self):
        """Return the front item without removing it"""
        if self.is_empty():                # Check if queue is empty
            return None                    # Return None if empty
        return self.items[0]               # Return first item
    
    # Lines 205-207: Check if empty method
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.items) == 0        # True if no items
    
    # Lines 209-211: Get size method
    def size(self):
        """Return the size of the queue"""
        return len(self.items)             # Return count of items
    
    # Lines 213-215: Clear method
    def clear(self):
        """Clear all items from the queue"""
        self.items = []                    # Reset to empty list

# Lines 217-313: StudentDataProcessor class (Utility operations)
class StudentDataProcessor:
    """Utility class for processing student data using custom data structures"""
    
    def __init__(self):                    # Constructor
        self.operation_history = Stack(50)  # Stack for last 50 operations
        self.batch_queue = Queue()         # Queue for batch processing
    
    # Lines 224-231: Log operation method
    def log_operation(self, operation_type, data):
        """Log an operation to the history stack"""
        operation = {                      # Create operation record
            'type': operation_type,
            'data': data,
            'timestamp': self._get_timestamp()
        }
        self.operation_history.push(operation)  # Add to history stack
    
    # Lines 233-236: Get operation history method
    def get_operation_history(self, limit=10):
        """Get recent operation history"""
        history = self.operation_history.to_list()  # Convert stack to list
        return history[:limit]             # Return limited results
    
    # Lines 238-253: Sort students by grade method
    def sort_students_by_grade(self, students):
        """Sort students by average grade using custom comparison"""
        def get_average_grade(student):    # Helper function
            grades = student.get('grades', [])
            return sum(grades) / len(grades) if grades else 0
        
        # Lines 244-252: Bubble sort implementation
        student_list = students.copy()     # Create copy to avoid modifying original
        n = len(student_list)              # Get list length
        
        for i in range(n):                 # Outer loop for passes
            for j in range(0, n - i - 1):  # Inner loop for comparisons
                if get_average_grade(student_list[j]) < get_average_grade(student_list[j + 1]):
                    student_list[j], student_list[j + 1] = student_list[j + 1], student_list[j]
                    # Swap students if first has lower grade
        
        return student_list                # Return sorted list
    
    # Lines 255-266: Group by course method
    def group_by_course(self, students):
        """Group students by courses they are enrolled in"""
        course_groups = {}                 # Initialize grouping dictionary
        
        for student in students:           # Process each student
            courses = student.get('courses', [])
            for course in courses:         # Process each course
                if course not in course_groups:  # Create group if new course
                    course_groups[course] = []
                course_groups[course].append(student)  # Add student to course group
        
        return course_groups               # Return grouped data
    
    # Lines 268-307: Calculate statistics method
    def calculate_statistics(self, students):
        """Calculate various statistics for student data"""
        if not students:                   # Handle empty input
            return {}
        
        # Lines 273-283: Initialize tracking variables
        total_students = len(students)
        all_grades = []                    # Collect all grades
        course_count = {}                  # Count course enrollments
        
        for student in students:           # Process each student
            grades = student.get('grades', [])
            all_grades.extend(grades)      # Add all grades to collection
            
            courses = student.get('courses', [])
            for course in courses:         # Count course enrollments
                course_count[course] = course_count.get(course, 0) + 1
        
        if not all_grades:                 # Handle case with no grades
            return {'total_students': total_students}
        
        # Lines 288-296: Calculate basic statistics
        avg_grade = sum(all_grades) / len(all_grades)
        min_grade = min(all_grades)
        max_grade = max(all_grades)
        
        # Calculate median grade
        sorted_grades = sorted(all_grades)
        n = len(sorted_grades)
        median_grade = (sorted_grades[n//2] + sorted_grades[(n-1)//2]) / 2
        
        # Lines 298-307: Return comprehensive statistics
        return {
            'total_students': total_students,
            'total_grades': len(all_grades),
            'average_grade': round(avg_grade, 2),
            'median_grade': round(median_grade, 2),
            'min_grade': min_grade,
            'max_grade': max_grade,
            'most_popular_course': max(course_count, key=course_count.get) if course_count else None,
            'course_distribution': course_count
        }
    
    # Lines 309-313: Get timestamp helper method
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime      # Import datetime module
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format timestamp
```

---

### 🎯 **4. student_manager.py** (Business Logic - 278 lines)

```python
# Lines 1-3: Module documentation and imports
"""
Student Manager class that handles all student operations using custom data structures
"""

# Lines 5-7: Import required modules
import json                                # For JSON file operations
import os                                 # For file system operations
from data_structures import LinkedList, Stack, StudentDataProcessor  # Custom data structures

# Lines 9-278: StudentManager class implementation
class StudentManager:
    """Manages student records using custom linked list and stack data structures"""
    
    # Lines 12-17: Constructor and initialization
    def __init__(self, data_file='student_data.json'):
        self.students = LinkedList()       # Main storage using custom LinkedList
        self.operation_history = Stack(100)  # Track last 100 operations
        self.processor = StudentDataProcessor()  # Utility processor
        self.data_file = data_file         # JSON file for persistence
        self.load_data()                   # Load existing data on startup
    
    # Lines 19-41: Add student method
    def add_student(self, student_data):
        """Add a new student to the system"""
        # Line 21-23: Check for duplicate roll number
        if self.students.find(student_data['roll_no']):
            return False                   # Reject duplicate
        
        # Lines 25-30: Log operation for undo functionality
        self.operation_history.push({
            'action': 'add',
            'data': student_data.copy(),   # Store copy of data
            'timestamp': self._get_timestamp()
        })
        
        # Lines 32-33: Add to linked list storage
        self.students.append(student_data)
        
        # Lines 35-36: Log in processor for statistics
        self.processor.log_operation('add_student', student_data)
        
        # Lines 38-40: Save to persistent storage
        self.save_data()
        return True                        # Success
    
    # Lines 43-45: Get single student method
    def get_student(self, roll_no):
        """Get a student by roll number"""
        return self.students.find(roll_no)  # Use LinkedList find method
    
    # Lines 47-49: Get all students method
    def get_all_students(self):
        """Get all students as a list"""
        return self.students.to_list()     # Convert LinkedList to Python list
    
    # Lines 51-78: Update student method
    def update_student(self, roll_no, new_data):
        """Update a student's information"""
        # Lines 53-56: Get current data for undo
        old_data = self.students.find(roll_no)
        if not old_data:
            return False                   # Student not found
        
        # Lines 58-65: Log operation with before/after data
        self.operation_history.push({
            'action': 'update',
            'roll_no': roll_no,
            'old_data': old_data.copy(),   # Store original for undo
            'new_data': new_data.copy(),   # Store new for reference
            'timestamp': self._get_timestamp()
        })
        
        # Lines 67-68: Perform update in LinkedList
        success = self.students.update(roll_no, new_data)
        
        # Lines 70-76: Log and save if successful
        if success:
            self.processor.log_operation('update_student', {
                'roll_no': roll_no,
                'old_data': old_data,
                'new_data': new_data
            })
            self.save_data()               # Persist changes
        
        return success
    
    # Lines 80-101: Delete student method
    def delete_student(self, roll_no):
        """Delete a student from the system"""
        # Lines 82-85: Get student data before deletion
        student_data = self.students.find(roll_no)
        if not student_data:
            return False                   # Student not found
        
        # Lines 87-92: Log operation for undo
        self.operation_history.push({
            'action': 'delete',
            'data': student_data.copy(),   # Store deleted data for undo
            'timestamp': self._get_timestamp()
        })
        
        # Lines 94-95: Perform deletion
        success = self.students.delete(roll_no)
        
        # Lines 97-100: Log and save if successful
        if success:
            self.processor.log_operation('delete_student', student_data)
            self.save_data()
        
        return success
    
    # Lines 103-105: Search students method
    def search_students(self, search_term):
        """Search students by name, email, or roll number"""
        return self.students.search(search_term)  # Use LinkedList search
    
    # Lines 107-109: Filter by course method
    def filter_by_course(self, course_name):
        """Get all students enrolled in a specific course"""
        return self.students.filter_by_course(course_name)
    
    # Lines 111-113: Filter by grade range method
    def filter_by_grade_range(self, min_grade, max_grade):
        """Get students within a specific grade range"""
        return self.students.filter_by_grade_range(min_grade, max_grade)
    
    # Lines 115-132: Get top performers method
    def get_top_performers(self, limit=10):
        """Get top performing students"""
        all_students = self.get_all_students()  # Get all student data
        
        # Lines 119-127: Calculate average grades and create enriched data
        students_with_avg = []
        for student in all_students:
            grades = student.get('grades', [])
            if grades:                     # Only include students with grades
                avg_grade = sum(grades) / len(grades)
                student_copy = student.copy()  # Don't modify original
                student_copy['avg_grade'] = round(avg_grade, 2)
                students_with_avg.append(student_copy)
        
        # Lines 129-131: Sort and limit results
        students_with_avg.sort(key=lambda x: x['avg_grade'], reverse=True)
        return students_with_avg[:limit]   # Return top N performers
    
    # Lines 134-146: Calculate overall average grade
    def calculate_average_grade(self):
        """Calculate overall average grade across all students"""
        all_students = self.get_all_students()
        all_grades = []                    # Collect all grades
        
        # Lines 139-141: Extract all grades from all students
        for student in all_students:
            grades = student.get('grades', [])
            all_grades.extend(grades)      # Add student's grades to collection
        
        # Lines 143-146: Calculate and return average
        if not all_grades:
            return 0                       # No grades found
        return round(sum(all_grades) / len(all_grades), 2)
    
    # Lines 148-175: Get course statistics method
    def get_course_statistics(self):
        """Get statistics for each course"""
        all_students = self.get_all_students()
        course_stats = {}                  # Initialize statistics container
        
        # Lines 153-168: Process each student's courses and grades
        for student in all_students:
            courses = student.get('courses', [])
            grades = student.get('grades', [])
            
            for course, grade in zip(courses, grades):  # Pair courses with grades
                if course not in course_stats:  # Initialize course if new
                    course_stats[course] = {
                        'students': [],
                        'grades': [],
                        'total_students': 0,
                        'avg_grade': 0
                    }
                
                # Lines 166-168: Add data to course statistics
                course_stats[course]['students'].append(student['name'])
                course_stats[course]['grades'].append(grade)
                course_stats[course]['total_students'] += 1
        
        # Lines 170-173: Calculate averages for each course
        for course in course_stats:
            grades = course_stats[course]['grades']
            course_stats[course]['avg_grade'] = round(sum(grades) / len(grades), 2)
        
        return course_stats
    
    # Lines 177-194: Get operation history method
    def get_operation_history(self, limit=10):
        """Get recent operation history"""
        history = []                       # Initialize results
        temp_stack = Stack()               # Temporary stack for preservation
        
        # Lines 182-188: Extract items from history stack
        count = 0
        while not self.operation_history.is_empty() and count < limit:
            operation = self.operation_history.pop()  # Get operation
            history.append(operation)      # Add to results
            temp_stack.push(operation)     # Save for restoration
            count += 1
        
        # Lines 190-192: Restore original stack
        while not temp_stack.is_empty():
            self.operation_history.push(temp_stack.pop())
        
        return history
    
    # Lines 196-226: Undo last operation method
    def undo_last_operation(self):
        """Undo the last operation (basic implementation)"""
        if self.operation_history.is_empty():  # Check if any operations to undo
            return False, "No operations to undo"
        
        last_operation = self.operation_history.pop()  # Get last operation
        action = last_operation.get('action')
        
        # Lines 204-220: Handle different operation types
        try:
            if action == 'add':            # Undo add by deleting
                roll_no = last_operation['data']['roll_no']
                self.students.delete(roll_no)
                
            elif action == 'delete':       # Undo delete by adding back
                self.students.append(last_operation['data'])
                
            elif action == 'update':       # Undo update by restoring old data
                roll_no = last_operation['roll_no']
                old_data = last_operation['old_data']
                self.students.update(roll_no, old_data)
            
            # Lines 220-221: Save changes and return success
            self.save_data()
            return True, f"Successfully undid {action} operation"
            
        # Lines 223-226: Handle undo failures
        except Exception as e:
            self.operation_history.push(last_operation)  # Restore operation to stack
            return False, f"Failed to undo operation: {str(e)}"
    
    # Lines 228-235: Save data to file method
    def save_data(self):
        """Save student data to JSON file"""
        try:
            students_list = self.get_all_students()  # Get all data
            with open(self.data_file, 'w') as f:     # Open file for writing
                json.dump(students_list, f, indent=2)  # Write formatted JSON
        except Exception as e:
            print(f"Error saving data: {e}")         # Log save errors
    
    # Lines 237-246: Load data from file method
    def load_data(self):
        """Load student data from JSON file"""
        try:
            if os.path.exists(self.data_file):       # Check if file exists
                with open(self.data_file, 'r') as f: # Open file for reading
                    students_list = json.load(f)     # Parse JSON data
                    for student in students_list:    # Add each student to LinkedList
                        self.students.append(student)
        except Exception as e:
            print(f"Error loading data: {e}")        # Log load errors
    
    # Lines 248-251: Get comprehensive statistics
    def get_statistics(self):
        """Get comprehensive statistics using the processor"""
        all_students = self.get_all_students()
        return self.processor.calculate_statistics(all_students)
    
    # Lines 253-255: Export to JSON method
    def export_to_json(self):
        """Export all student data to JSON format"""
        return json.dumps(self.get_all_students(), indent=2)
    
    # Lines 257-272: Import from JSON method
    def import_from_json(self, json_data):
        """Import student data from JSON format"""
        try:
            students_list = json.loads(json_data)    # Parse JSON string
            imported_count = 0                       # Track successful imports
            
            for student_data in students_list:       # Process each student
                if self.add_student(student_data):    # Attempt to add
                    imported_count += 1               # Count success
            
            return imported_count, len(students_list)  # Return counts
            
        # Lines 269-272: Handle import errors
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        except Exception as e:
            raise ValueError(f"Import error: {str(e)}")
    
    # Lines 274-277: Get timestamp helper method
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

---

### 🔍 **5. query_engine.py** (SQL-like Query Processing - 315 lines)

```python
# Lines 1-4: Module documentation and imports
"""
SQL-like query engine for student records
Supports basic SELECT, WHERE, ORDER BY operations
"""

# Lines 6-7: Import required modules
import re                                  # For regular expression parsing
from datetime import datetime             # For timestamp operations

# Lines 9-315: QueryEngine class implementation
class QueryEngine:
    """SQL-like query engine for student data"""
    
    # Lines 12-16: Constructor and supported operations
    def __init__(self, student_manager):
        self.student_manager = student_manager  # Reference to student data
        self.supported_operations = [           # List of supported SQL operations
            'SELECT', 'WHERE', 'ORDER BY', 'LIMIT', 'GROUP BY'
        ]
    
    # Lines 18-54: Main query execution method
    def execute_query(self, query_string):
        """Execute a SQL-like query on student data"""
        try:
            # Lines 21-22: Normalize query for processing
            query = query_string.strip().upper()
            
            # Lines 24-25: Parse query into components
            parsed_query = self._parse_query(query)
            
            # Lines 27-28: Get base dataset
            students = self.student_manager.get_all_students()
            
            # Lines 30-32: Apply WHERE clause filtering
            if 'WHERE' in parsed_query:
                students = self._apply_where_clause(students, parsed_query['WHERE'])
            
            # Lines 34-36: Apply GROUP BY operation
            if 'GROUP BY' in parsed_query:
                return self._apply_group_by(students, parsed_query['GROUP BY'])
            
            # Lines 38-40: Apply ORDER BY sorting
            if 'ORDER BY' in parsed_query:
                students = self._apply_order_by(students, parsed_query['ORDER BY'])
            
            # Lines 42-45: Apply LIMIT restriction
            if 'LIMIT' in parsed_query:
                limit = int(parsed_query['LIMIT'])
                students = students[:limit]
            
            # Lines 47-49: Apply SELECT column filtering
            if 'SELECT' in parsed_query and parsed_query['SELECT'] != '*':
                students = self._apply_select(students, parsed_query['SELECT'])
            
            return students                # Return processed results
            
        # Lines 53-54: Handle query execution errors
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")
    
    # Lines 56-90: Query parsing method
    def _parse_query(self, query):
        """Parse SQL-like query into components"""
        parsed = {}                        # Initialize parsed components
        
        # Lines 60-61: Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Lines 63-68: Extract SELECT clause
        select_match = re.search(r'SELECT\s+(.+?)(?:\s+FROM|$)', query)
        if select_match:
            parsed['SELECT'] = select_match.group(1).strip()
        else:
            raise Exception("Invalid query: Missing SELECT clause")
        
        # Lines 70-73: Extract WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+ORDER BY|\s+GROUP BY|\s+LIMIT|$)', query)
        if where_match:
            parsed['WHERE'] = where_match.group(1).strip()
        
        # Lines 75-78: Extract ORDER BY clause
        order_match = re.search(r'ORDER BY\s+(.+?)(?:\s+LIMIT|$)', query)
        if order_match:
            parsed['ORDER BY'] = order_match.group(1).strip()
        
        # Lines 80-83: Extract GROUP BY clause
        group_match = re.search(r'GROUP BY\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|$)', query)
        if group_match:
            parsed['GROUP BY'] = group_match.group(1).strip()
        
        # Lines 85-88: Extract LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', query)
        if limit_match:
            parsed['LIMIT'] = limit_match.group(1).strip()
        
        return parsed                      # Return parsed components
    
    # Lines 92-100: Apply WHERE clause method
    def _apply_where_clause(self, students, where_clause):
        """Apply WHERE conditions to filter students"""
        filtered_students = []             # Initialize results
        
        for student in students:           # Process each student
            if self._evaluate_condition(student, where_clause):  # Check condition
                filtered_students.append(student)  # Add if matches
        
        return filtered_students
    
    # Lines 102-113: Evaluate condition method
    def _evaluate_condition(self, student, condition):
        """Evaluate a WHERE condition for a single student"""
        # Lines 104-107: Handle AND operator
        if ' AND ' in condition:
            conditions = condition.split(' AND ')
            return all(self._evaluate_single_condition(student, cond.strip()) for cond in conditions)
        
        # Lines 109-112: Handle OR operator
        if ' OR ' in condition:
            conditions = condition.split(' OR ')
            return any(self._evaluate_single_condition(student, cond.strip()) for cond in conditions)
        
        return self._evaluate_single_condition(student, condition)
    
    # Lines 115-129: Evaluate single condition method
    def _evaluate_single_condition(self, student, condition):
        """Evaluate a single condition"""
        # Lines 117-118: Define supported operators
        operators = ['>=', '<=', '!=', '=', '>', '<', 'LIKE', 'IN']
        
        # Lines 120-128: Parse condition and evaluate
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)    # Split on first occurrence
                if len(parts) == 2:
                    field = parts[0].strip()       # Left side: field name
                    value = parts[1].strip().strip("'\"")  # Right side: value
                    
                    return self._compare_values(student, field, op, value)
        
        raise Exception(f"Invalid condition: {condition}")
    
    # Lines 131-184: Compare values method
    def _compare_values(self, student, field, operator, value):
        """Compare student field value with condition value"""
        # Lines 133-134: Get field value from student
        student_value = self._get_field_value(student, field)
        
        # Lines 136-137: Handle null values
        if student_value is None:
            return False
        
        # Lines 139-183: Handle different operators
        try:
            if operator == '=':            # Equality comparison
                return str(student_value).upper() == str(value).upper()
            
            elif operator == '!=':         # Inequality comparison
                return str(student_value).upper() != str(value).upper()
            
            elif operator == 'LIKE':       # Substring search
                return value.upper() in str(student_value).upper()
            
            elif operator in ['>', '<', '>=', '<=']:  # Numeric/string comparison
                # Lines 151-164: Try numeric comparison first
                try:
                    num_student = float(student_value)
                    num_value = float(value)
                    
                    if operator == '>':
                        return num_student > num_value
                    elif operator == '<':
                        return num_student < num_value
                    elif operator == '>=':
                        return num_student >= num_value
                    elif operator == '<=':
                        return num_student <= num_value
                        
                # Lines 165-174: Fall back to string comparison
                except ValueError:
                    if operator == '>':
                        return str(student_value) > str(value)
                    elif operator == '<':
                        return str(student_value) < str(value)
                    elif operator == '>=':
                        return str(student_value) >= str(value)
                    elif operator == '<=':
                        return str(student_value) <= str(value)
            
            elif operator == 'IN':         # Multiple value matching
                # Lines 177-179: Parse comma-separated values
                values = [v.strip().strip("'\"") for v in value.split(',')]
                return str(student_value).upper() in [v.upper() for v in values]
            
        # Lines 181-182: Handle comparison errors
        except Exception:
            return False
        
        return False
    
    # Lines 186-207: Get field value method
    def _get_field_value(self, student, field):
        """Get field value from student record"""
        field = field.upper()              # Normalize field name
        
        # Lines 190-206: Map field names to student data
        if field == 'ROLL_NO':
            return student.get('roll_no')
        elif field == 'NAME':
            return student.get('name')
        elif field == 'EMAIL':
            return student.get('email')
        elif field == 'COURSES':
            return ', '.join(student.get('courses', []))
        elif field == 'GRADES':
            return ', '.join(map(str, student.get('grades', [])))
        elif field == 'AVG_GRADE':        # Calculated field
            grades = student.get('grades', [])
            return sum(grades) / len(grades) if grades else 0
        elif field == 'COURSE_COUNT':     # Calculated field
            return len(student.get('courses', []))
        else:
            return student.get(field.lower())  # Try direct field access
    
    # Lines 209-236: Apply ORDER BY method
    def _apply_order_by(self, students, order_clause):
        """Apply ORDER BY clause to sort students"""
        parts = order_clause.split()       # Split clause into components
        field = parts[0]                   # First part is field name
        direction = 'ASC'                  # Default sort direction
        
        # Lines 214-216: Parse sort direction
        if len(parts) > 1 and parts[1].upper() in ['ASC', 'DESC']:
            direction = parts[1].upper()
        
        # Lines 218-235: Perform sorting
        try:
            reverse = (direction == 'DESC')  # Determine sort order
            
            # Lines 222-231: Define sort key function
            def sort_key(student):
                value = self._get_field_value(student, field)
                if value is None:
                    return ''              # Handle null values
                
                # Lines 227-230: Try numeric sort, fall back to string
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return str(value).upper()
            
            return sorted(students, key=sort_key, reverse=reverse)
            
        # Lines 234-236: Handle sorting errors
        except Exception as e:
            raise Exception(f"Error in ORDER BY: {str(e)}")
    
    # Lines 238-262: Apply GROUP BY method
    def _apply_group_by(self, students, group_clause):
        """Apply GROUP BY clause to group students"""
        field = group_clause.strip()       # Get grouping field
        groups = {}                        # Initialize groups container
        
        # Lines 243-249: Group students by field value
        for student in students:
            group_value = self._get_field_value(student, field)
            if group_value is None:
                group_value = 'NULL'       # Handle null values
            
            group_key = str(group_value)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(student)
        
        # Lines 254-261: Format grouped results
        result = []
        for group_name, group_students in groups.items():
            result.append({
                'group': group_name,
                'count': len(group_students),
                'students': group_students
            })
        
        return result
    
    # Lines 264-280: Apply SELECT method
    def _apply_select(self, students, select_clause):
        """Apply SELECT clause to filter columns"""
        if select_clause == '*':           # Return all columns
            return students
        
        # Lines 270-279: Parse selected fields and filter
        fields = [field.strip().upper() for field in select_clause.split(',')]
        
        filtered_students = []
        for student in students:
            filtered_student = {}          # Create new student record
            for field in fields:           # Include only selected fields
                value = self._get_field_value(student, field)
                filtered_student[field.lower()] = value
            filtered_students.append(filtered_student)
        
        return filtered_students
    
    # Lines 282-294: Get sample queries method
    def get_sample_queries(self):
        """Get sample queries for user reference"""
        return [                           # Return list of example queries
            "SELECT * FROM students",
            "SELECT name, avg_grade FROM students WHERE avg_grade > 80",
            "SELECT * FROM students WHERE name LIKE 'John'",
            "SELECT * FROM students WHERE avg_grade >= 70 AND avg_grade <= 90",
            "SELECT * FROM students ORDER BY avg_grade DESC",
            "SELECT * FROM students ORDER BY name ASC LIMIT 5",
            "SELECT name FROM students WHERE courses LIKE 'Math'",
            "GROUP BY courses",
            "SELECT * FROM students WHERE course_count > 2"
        ]
    
    # Lines 296-314: Validate query method
    def validate_query(self, query_string):
        """Validate query syntax"""
        query = query_string.strip().upper()  # Normalize query
        
        # Lines 300-302: Check for SELECT clause
        if not query.startswith('SELECT'):
            return False, "Query must start with SELECT"
        
        # Lines 304-306: Check for SELECT presence
        if 'SELECT' not in query:
            return False, "Missing SELECT clause"
        
        # Lines 308-312: Check for unsupported operations
        unsupported = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE']
        for op in unsupported:
            if op in query:
                return False, f"Unsupported operation: {op}"
        
        return True, "Query is valid"      # All validations passed
```

---

### 🎨 **6. templates/base.html** (Base Template - 127 lines)

```html
<!-- Lines 1-2: HTML5 document declaration with dark theme -->
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">

<!-- Lines 3-16: HTML head section with metadata and external resources -->
<head>
    <meta charset="UTF-8">                    <!-- Character encoding -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  <!-- Responsive viewport -->
    <title>{% block title %}Student Record Management System{% endblock %}</title>  <!-- Dynamic title -->
    
    <!-- Line 8-9: Bootstrap CSS for styling framework -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Lines 11-12: Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <!-- Lines 14-15: Custom CSS for dark theme -->
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>

<!-- Lines 17-71: HTML body with navigation -->
<body>
    <!-- Lines 18-71: Navigation bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom">
        <div class="container-fluid">
            <!-- Lines 21-24: Brand/logo section -->
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">
                <i class="fas fa-graduation-cap me-2"></i>  <!-- Graduation cap icon -->
                Student Records
            </a>
            
            <!-- Lines 26-28: Mobile menu toggle button -->
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <!-- Lines 30-70: Collapsible navigation menu -->
            <div class="collapse navbar-collapse" id="navbarNav">
                <!-- Lines 31-52: Main navigation links -->
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('index') }}">
                            <i class="fas fa-home me-1"></i>Dashboard  <!-- Home icon + Dashboard -->
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('add_student') }}">
                            <i class="fas fa-user-plus me-1"></i>Add Student  <!-- User plus icon -->
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('query') }}">
                            <i class="fas fa-search me-1"></i>Query  <!-- Search icon -->
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('reports') }}">
                            <i class="fas fa-chart-bar me-1"></i>Reports  <!-- Chart icon -->
                        </a>
                    </li>
                </ul>
                
                <!-- Lines 54-68: Search form and export button -->
                <form class="d-flex me-3" method="GET" action="{{ url_for('search') }}">
                    <div class="input-group">
                        <!-- Search input with preserved value -->
                        <input class="form-control" type="search" name="search" placeholder="Search students..." 
                               value="{{ request.args.get('search', '') }}">
                        <button class="btn btn-outline-light" type="submit">
                            <i class="fas fa-search"></i>  <!-- Search icon -->
                        </button>
                    </div>
                </form>
                
                <!-- Export button -->
                <a href="{{ url_for('export_data') }}" class="btn btn-outline-success btn-sm">
                    <i class="fas fa-download me-1"></i>Export  <!-- Download icon -->
                </a>
            </div>
        </div>
    </nav>

    <!-- Lines 73-92: Flash message display system -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container-fluid mt-3">
                {% for category, message in messages %}  <!-- Loop through messages -->
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        <!-- Lines 78-85: Icon selection based on message category -->
                        {% if category == 'success' %}
                            <i class="fas fa-check-circle me-2"></i>      <!-- Success icon -->
                        {% elif category == 'error' %}
                            <i class="fas fa-exclamation-triangle me-2"></i>  <!-- Error icon -->
                        {% elif category == 'info' %}
                            <i class="fas fa-info-circle me-2"></i>       <!-- Info icon -->
                        {% endif %}
                        {{ message }}  <!-- Display message text -->
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>  <!-- Close button -->
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Lines 94-97: Main content area -->
    <div class="container-fluid py-4">
        {% block content %}{% endblock %}  <!-- Placeholder for page-specific content -->
    </div>

    <!-- Lines 99-116: Footer section -->
    <footer class="bg-dark text-light py-3 mt-5">
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-6">
                    <p class="mb-0">
                        <i class="fas fa-graduation-cap me-2"></i>  <!-- Graduation cap icon -->
                        Student Record Management System
                    </p>
                </div>
                <div class="col-md-6 text-end">
                    <small class="text-muted">
                        Powered by Flask & Python Data Structures  <!-- Technology credit -->
                    </small>
                </div>
            </div>
        </div>
    </footer>

    <!-- Lines 118-124: JavaScript includes -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>  <!-- Bootstrap JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>  <!-- Custom JavaScript -->
    
    {% block scripts %}{% endblock %}  <!-- Placeholder for page-specific scripts -->
</body>
</html>
```

---

## 🎨 **STATIC FILES EXPLANATION**

### **static/css/style.css** (Dark Theme Styling)
- **Lines 1-20**: CSS variables for consistent dark theme colors
- **Lines 23-28**: Global body styling with dark background
- **Lines 30-68**: Enhanced navigation with gradients and hover effects
- **Lines 70-98**: Card styling with dark theme and hover animations
- **Lines 100-159**: Button styling with gradients and hover effects
- **Lines 161-191**: Form control styling for dark theme
- **Lines 193-223**: Table styling with dark colors and hover effects
- **Lines 225-258**: Badge styling with gradient backgrounds
- **Lines 260-290**: Alert styling with dark theme colors

### **static/js/main.js** (Interactive Functionality)
- **Lines 1-157**: Utility functions for common operations
- **Lines 159-326**: Form validation with real-time feedback
- **Lines 328-492**: Search and table filtering functionality
- **Lines 494-607**: Dashboard animations and statistics
- **Lines 609-700**: Query interface with syntax highlighting
- **Lines 702-800**: Interactive features and user experience

---

## 🏗️ **ARCHITECTURE SUMMARY**

### **Data Flow:**
1. **User Input** → Flask Routes → Validation → Business Logic
2. **Business Logic** → Custom Data Structures → JSON Persistence
3. **Query Processing** → LinkedList Traversal → Filtered Results
4. **Statistics** → Data Aggregation → Chart Rendering

### **Key Design Patterns:**
- **MVC Architecture**: Separation of models, views, and controllers
- **Custom Data Structures**: LinkedList, Stack, Queue implementations
- **Template Inheritance**: Base template with extended child templates
- **Component-Based CSS**: Modular styling with reusable classes
- **Progressive Enhancement**: JavaScript adds functionality to HTML base

### **Technology Stack:**
- **Backend**: Python Flask with custom data structures
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Bootstrap 5 + Custom Dark Theme
- **Data Storage**: JSON file persistence
- **Query Engine**: Custom SQL-like parser and processor

This comprehensive mind map and code explanation covers every aspect of your Student Record Management System, from the high-level architecture down to individual line explanations for each file.