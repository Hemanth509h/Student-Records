"""
SQL-like query engine for student records
Supports basic SELECT, WHERE, ORDER BY operations
"""

import re
from datetime import datetime

class QueryEngine:
    """SQL-like query engine for student data"""
    
    def __init__(self, student_manager):
        self.student_manager = student_manager
        self.supported_operations = [
            'SELECT', 'WHERE', 'ORDER BY', 'LIMIT', 'GROUP BY'
        ]
    
    def execute_query(self, query_string):
        """Execute a SQL-like query on student data"""
        try:
            # Normalize query
            query = query_string.strip().upper()
            
            # Parse query components
            parsed_query = self._parse_query(query)
            
            # Get base data
            students = self.student_manager.get_all_students()
            
            # Apply WHERE clause
            if 'WHERE' in parsed_query:
                students = self._apply_where_clause(students, parsed_query['WHERE'])
            
            # Apply GROUP BY
            if 'GROUP BY' in parsed_query:
                return self._apply_group_by(students, parsed_query['GROUP BY'])
            
            # Apply ORDER BY
            if 'ORDER BY' in parsed_query:
                students = self._apply_order_by(students, parsed_query['ORDER BY'])
            
            # Apply LIMIT
            if 'LIMIT' in parsed_query:
                limit = int(parsed_query['LIMIT'])
                students = students[:limit]
            
            # Apply SELECT (column filtering)
            if 'SELECT' in parsed_query and parsed_query['SELECT'] != '*':
                students = self._apply_select(students, parsed_query['SELECT'])
            
            return students
            
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")
    
    def _parse_query(self, query):
        """Parse SQL-like query into components"""
        parsed = {}
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Extract SELECT clause
        select_match = re.search(r'SELECT\s+(.+?)(?:\s+FROM|$)', query)
        if select_match:
            parsed['SELECT'] = select_match.group(1).strip()
        else:
            raise Exception("Invalid query: Missing SELECT clause")
        
        # Extract WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+ORDER BY|\s+GROUP BY|\s+LIMIT|$)', query)
        if where_match:
            parsed['WHERE'] = where_match.group(1).strip()
        
        # Extract ORDER BY clause
        order_match = re.search(r'ORDER BY\s+(.+?)(?:\s+LIMIT|$)', query)
        if order_match:
            parsed['ORDER BY'] = order_match.group(1).strip()
        
        # Extract GROUP BY clause
        group_match = re.search(r'GROUP BY\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|$)', query)
        if group_match:
            parsed['GROUP BY'] = group_match.group(1).strip()
        
        # Extract LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', query)
        if limit_match:
            parsed['LIMIT'] = limit_match.group(1).strip()
        
        return parsed
    
    def _apply_where_clause(self, students, where_clause):
        """Apply WHERE conditions to filter students"""
        filtered_students = []
        
        for student in students:
            if self._evaluate_condition(student, where_clause):
                filtered_students.append(student)
        
        return filtered_students
    
    def _evaluate_condition(self, student, condition):
        """Evaluate a WHERE condition for a single student"""
        # Handle AND/OR operators
        if ' AND ' in condition:
            conditions = condition.split(' AND ')
            return all(self._evaluate_single_condition(student, cond.strip()) for cond in conditions)
        
        if ' OR ' in condition:
            conditions = condition.split(' OR ')
            return any(self._evaluate_single_condition(student, cond.strip()) for cond in conditions)
        
        return self._evaluate_single_condition(student, condition)
    
    def _evaluate_single_condition(self, student, condition):
        """Evaluate a single condition"""
        # Parse condition (field operator value)
        operators = ['>=', '<=', '!=', '=', '>', '<', 'LIKE', 'IN']
        
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value = parts[1].strip().strip("'\"")
                    
                    return self._compare_values(student, field, op, value)
        
        raise Exception(f"Invalid condition: {condition}")
    
    def _compare_values(self, student, field, operator, value):
        """Compare student field value with condition value"""
        # Get student field value
        student_value = self._get_field_value(student, field)
        
        if student_value is None:
            return False
        
        try:
            # Handle different operators
            if operator == '=':
                return str(student_value).upper() == str(value).upper()
            
            elif operator == '!=':
                return str(student_value).upper() != str(value).upper()
            
            elif operator == 'LIKE':
                return value.upper() in str(student_value).upper()
            
            elif operator in ['>', '<', '>=', '<=']:
                # Try numeric comparison
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
                        
                except ValueError:
                    # String comparison
                    if operator == '>':
                        return str(student_value) > str(value)
                    elif operator == '<':
                        return str(student_value) < str(value)
                    elif operator == '>=':
                        return str(student_value) >= str(value)
                    elif operator == '<=':
                        return str(student_value) <= str(value)
            
            elif operator == 'IN':
                # Handle IN operator (value should be comma-separated)
                values = [v.strip().strip("'\"") for v in value.split(',')]
                return str(student_value).upper() in [v.upper() for v in values]
            
        except Exception:
            return False
        
        return False
    
    def _get_field_value(self, student, field):
        """Get field value from student record"""
        field = field.upper()
        
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
        elif field == 'AVG_GRADE':
            grades = student.get('grades', [])
            return sum(grades) / len(grades) if grades else 0
        elif field == 'COURSE_COUNT':
            return len(student.get('courses', []))
        else:
            # Try to get the field directly
            return student.get(field.lower())
    
    def _apply_order_by(self, students, order_clause):
        """Apply ORDER BY clause to sort students"""
        parts = order_clause.split()
        field = parts[0]
        direction = 'ASC'
        
        if len(parts) > 1 and parts[1].upper() in ['ASC', 'DESC']:
            direction = parts[1].upper()
        
        # Sort students
        try:
            reverse = (direction == 'DESC')
            
            def sort_key(student):
                value = self._get_field_value(student, field)
                if value is None:
                    return ''
                
                # Try to convert to number for numeric sorting
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return str(value).upper()
            
            return sorted(students, key=sort_key, reverse=reverse)
            
        except Exception as e:
            raise Exception(f"Error in ORDER BY: {str(e)}")
    
    def _apply_group_by(self, students, group_clause):
        """Apply GROUP BY clause to group students"""
        field = group_clause.strip()
        groups = {}
        
        for student in students:
            group_value = self._get_field_value(student, field)
            if group_value is None:
                group_value = 'NULL'
            
            group_key = str(group_value)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(student)
        
        # Return grouped results
        result = []
        for group_name, group_students in groups.items():
            result.append({
                'group': group_name,
                'count': len(group_students),
                'students': group_students
            })
        
        return result
    
    def _apply_select(self, students, select_clause):
        """Apply SELECT clause to filter columns"""
        if select_clause == '*':
            return students
        
        # Parse selected fields
        fields = [field.strip().upper() for field in select_clause.split(',')]
        
        filtered_students = []
        for student in students:
            filtered_student = {}
            for field in fields:
                value = self._get_field_value(student, field)
                filtered_student[field.lower()] = value
            filtered_students.append(filtered_student)
        
        return filtered_students
    
    def get_sample_queries(self):
        """Get sample queries for user reference"""
        return [
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
    
    def validate_query(self, query_string):
        """Validate query syntax"""
        query = query_string.strip().upper()
        
        # Check if query starts with SELECT
        if not query.startswith('SELECT'):
            return False, "Query must start with SELECT"
        
        # Check for basic syntax
        if 'SELECT' not in query:
            return False, "Missing SELECT clause"
        
        # Check for unsupported operations
        unsupported = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE']
        for op in unsupported:
            if op in query:
                return False, f"Unsupported operation: {op}"
        
        return True, "Query is valid"
