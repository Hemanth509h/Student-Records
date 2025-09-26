#!/usr/bin/env python3
"""
Student Data Generator Script
=============================

This script generates and inserts 3000 sample students into the database
for testing and demonstration purposes.

Usage:
    python add_students.py

This will add 3000 students with realistic sample data.
"""

import os
import sys
import random
from datetime import datetime, date
from typing import List, Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.models import db, Student
    from core.app import app
    print("✓ Successfully imported all required modules")
except ImportError as e:
    print(f"✗ Error importing modules: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


# Sample data for generating realistic students
FIRST_NAMES = [
    # Male names
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Krishna", 
    "Ishaan", "Shaurya", "Atharv", "Advait", "Vedant", "Kabir", "Aryan", "Yuvaan",
    "Daksh", "Grayson", "Liam", "Noah", "Oliver", "James", "Benjamin", "Lucas",
    "Henry", "Alexander", "Mason", "Michael", "Ethan", "Daniel", "Jacob", "Logan",
    "Jackson", "Levi", "Sebastian", "Mateo", "Jack", "Owen", "Theodore", "Aiden",
    
    # Female names  
    "Saanvi", "Ananya", "Diya", "Aanya", "Pihu", "Aadhya", "Inaya", "Prisha",
    "Kavya", "Arya", "Myra", "Sara", "Mira", "Anaya", "Pari", "Ira", "Riya",
    "Avni", "Kyra", "Veda", "Olivia", "Emma", "Charlotte", "Amelia", "Ava",
    "Sophia", "Isabella", "Mia", "Evelyn", "Harper", "Luna", "Camila", "Gianna",
    "Elizabeth", "Eleanor", "Ella", "Abigail", "Sofia", "Avery", "Scarlett", "Emily"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Agarwal", "Jain", "Bansal", 
    "Garg", "Mittal", "Goyal", "Jindal", "Arora", "Chopra", "Malhotra", "Kapoor",
    "Khanna", "Bhatia", "Sethi", "Mehta", "Shah", "Patel", "Modi", "Joshi",
    "Tiwari", "Dubey", "Mishra", "Pandey", "Yadav", "Chauhan", "Rajput", "Thakur",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzales", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"
]

COURSES = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
    "English Literature", "History", "Geography", "Economics", "Psychology",
    "Art", "Music", "Physical Education", "Foreign Language", "Philosophy",
    "Sociology", "Political Science", "Statistics", "Environmental Science", "Business Studies"
]

DEPARTMENTS = ["Science", "Arts", "Commerce", "Engineering", "Medical"]
GRADES_RANGE = [(60, 100), (70, 95), (50, 85), (40, 90), (80, 100)]  # Different performance levels


def generate_student_data() -> Dict[str, Any]:
    """Generate realistic student data"""
    
    # Random name combination
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Generate roll number
    roll_prefix = random.choice(['CS', 'EC', 'ME', 'CE', 'IT'])
    roll_number = f"{roll_prefix}{random.randint(2020, 2024)}{random.randint(1000, 9999)}"
    
    # Generate email
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@school.edu"
    
    # Generate random courses (3-6 courses per student)
    num_courses = random.randint(3, 6)
    student_courses = random.sample(COURSES, num_courses)
    
    # Generate grades based on performance level
    performance_level = random.choice(GRADES_RANGE)
    grades = []
    for _ in range(num_courses):
        grade = round(random.uniform(performance_level[0], performance_level[1]), 2)
        grades.append(grade)
    
    return {
        'roll_no': roll_number,
        'name': f"{first_name} {last_name}",
        'email': email,
        'courses': student_courses,
        'grades': grades
    }


def check_existing_students() -> int:
    """Check how many students already exist"""
    try:
        with app.app_context():
            count = Student.query.count()
            return count
    except Exception as e:
        print(f"Error checking existing students: {e}")
        return 0


def bulk_insert_students(students_data: List[Dict[str, Any]], batch_size: int = 500) -> bool:
    """Insert students in batches for better performance"""
    
    print(f"\n📝 Inserting {len(students_data)} students in batches of {batch_size}...")
    
    try:
        with app.app_context():
            total_inserted = 0
            
            # Process in batches
            for i in range(0, len(students_data), batch_size):
                batch = students_data[i:i + batch_size]
                batch_students = []
                
                for student_data in batch:
                    student = Student(
                        roll_no=student_data['roll_no'],
                        name=student_data['name'],
                        email=student_data['email'],
                        courses=student_data['courses'],
                        grades=student_data['grades']
                    )
                    batch_students.append(student)
                
                # Add batch to session
                db.session.add_all(batch_students)
                
                try:
                    db.session.commit()
                    total_inserted += len(batch)
                    print(f"  ✓ Inserted batch {i//batch_size + 1}: {len(batch)} students (Total: {total_inserted})")
                
                except Exception as e:
                    print(f"  ✗ Error inserting batch {i//batch_size + 1}: {e}")
                    db.session.rollback()
                    # Continue with next batch
                    continue
            
            print(f"\n✅ Successfully inserted {total_inserted} students!")
            return True
            
    except Exception as e:
        print(f"✗ Error in bulk insert: {e}")
        return False


def generate_unique_students(target_count: int, existing_count: int = 0) -> List[Dict[str, Any]]:
    """Generate unique student data, avoiding duplicates"""
    
    students_to_generate = target_count - existing_count
    if students_to_generate <= 0:
        print(f"✓ Already have {existing_count} students, no new students needed")
        return []
    
    print(f"\n🎲 Generating {students_to_generate} unique student records...")
    
    students_data = []
    used_roll_numbers = set()
    used_emails = set()
    
    attempts = 0
    max_attempts = students_to_generate * 3  # Allow some retries for uniqueness
    
    while len(students_data) < students_to_generate and attempts < max_attempts:
        student_data = generate_student_data()
        attempts += 1
        
        # Check for uniqueness
        if (student_data['roll_no'] not in used_roll_numbers and 
            student_data['email'] not in used_emails):
            
            students_data.append(student_data)
            used_roll_numbers.add(student_data['roll_no'])
            used_emails.add(student_data['email'])
            
            # Progress indicator
            if len(students_data) % 500 == 0:
                print(f"  Generated {len(students_data)}/{students_to_generate} students...")
    
    if len(students_data) < students_to_generate:
        print(f"⚠️  Could only generate {len(students_data)} unique students out of {students_to_generate} requested")
    else:
        print(f"✓ Generated {len(students_data)} unique student records")
    
    return students_data


def show_sample_data(students_data: List[Dict[str, Any]], count: int = 5) -> None:
    """Show sample generated data"""
    
    print(f"\n📋 Sample of generated student data (first {count} students):")
    print("-" * 80)
    
    for i, student in enumerate(students_data[:count]):
        print(f"\nStudent {i+1}:")
        print(f"  Roll No: {student['roll_no']}")
        print(f"  Name: {student['name']}")
        print(f"  Email: {student['email']}")
        print(f"  Courses: {', '.join(student['courses'])}")
        print(f"  Grades: {student['grades']}")
        print(f"  Average: {sum(student['grades'])/len(student['grades']):.2f}")


def show_statistics(students_data: List[Dict[str, Any]]) -> None:
    """Show statistics about the generated data"""
    
    if not students_data:
        return
    
    print(f"\n📊 Data Statistics:")
    print("-" * 40)
    
    # Course enrollment statistics
    course_counts = {}
    all_grades = []
    
    for student in students_data:
        for course in student['courses']:
            course_counts[course] = course_counts.get(course, 0) + 1
        all_grades.extend(student['grades'])
    
    print(f"Total Students: {len(students_data)}")
    print(f"Average Courses per Student: {sum(len(s['courses']) for s in students_data) / len(students_data):.1f}")
    print(f"Overall Grade Average: {sum(all_grades) / len(all_grades):.2f}")
    
    print(f"\nMost Popular Courses:")
    sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
    for course, count in sorted_courses[:5]:
        print(f"  {course}: {count} students")


def main() -> None:
    """Main function to add 3000 students"""
    
    print("🚀 Starting Student Data Generation")
    print("=" * 50)
    
    # Check database connection
    print("\n🔌 Checking database connection...")
    try:
        with app.app_context():
            # Test database connection
            db.session.execute(db.text("SELECT 1"))
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Make sure the database is running and create_tables.py has been executed")
        sys.exit(1)
    
    # Check existing students
    print("\n📊 Checking existing student data...")
    existing_count = check_existing_students()
    print(f"✓ Found {existing_count} existing students in database")
    
    target_count = 3000
    
    if existing_count >= target_count:
        print(f"✅ Already have {existing_count} students (target: {target_count})")
        print("No additional students needed!")
        return
    
    # Generate student data
    students_data = generate_unique_students(target_count, existing_count)
    
    if not students_data:
        print("No students to add!")
        return
    
    # Show sample data
    show_sample_data(students_data)
    
    # Insert students
    success = bulk_insert_students(students_data)
    
    if success:
        # Show final statistics
        final_count = check_existing_students()
        print(f"\n🎉 SUCCESS! Database now contains {final_count} students")
        
        # Show data statistics
        show_statistics(students_data)
        
        print(f"\n💡 Next steps:")
        print("  1. Start your application: python main.py")
        print("  2. Login with admin@school.com / admin123")
        print("  3. View all the generated student data")
        print("  4. Test the search and filtering features")
        
    else:
        print("\n❌ Failed to insert all students. Check the logs above for errors.")


if __name__ == "__main__":
    main()