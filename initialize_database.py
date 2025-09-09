#!/usr/bin/env python3
"""
Database Initialization Script for Student Record Management System
Run this script to populate the database with sample student data.
Use: python initialize_database.py
"""

import sys
import os

# Add the core directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.student_manager import StudentManager

def initialize_sample_data(force_overwrite=False):
    """Initialize the database with comprehensive sample student data"""
    
    print("🎓 Initializing Student Record Management System Database...")
    print("=" * 60)
    
    # Create student manager instance
    manager = StudentManager()
    
    # Check if database already has data
    existing_students = manager.get_all_students()
    if existing_students and not force_overwrite:
        print(f"⚠️  Database already contains {len(existing_students)} students.")
        try:
            choice = input("Do you want to overwrite existing data? (y/N): ").lower().strip()
            if choice != 'y':
                print("❌ Database initialization cancelled.")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Database initialization cancelled.")
            return False
        
        # Clear existing data
        print("🗑️  Clearing existing data...")
        for student in existing_students:
            manager.delete_student(student['roll_no'])
    
    # Sample student data with realistic academic information
    sample_students = [
        {
            'roll_no': 'CS001',
            'name': 'Alice Johnson',
            'email': 'alice.johnson@university.edu',
            'courses': ['Computer Science', 'Mathematics', 'Physics'],
            'grades': [88, 92, 85]
        },
        {
            'roll_no': 'CS002',
            'name': 'Bob Smith',
            'email': 'bob.smith@university.edu',
            'courses': ['Computer Science', 'Statistics', 'English'],
            'grades': [90, 78, 82]
        },
        {
            'roll_no': 'EE003',
            'name': 'Carol Williams',
            'email': 'carol.williams@university.edu',
            'courses': ['Electrical Engineering', 'Mathematics', 'Physics'],
            'grades': [95, 87, 91]
        },
        {
            'roll_no': 'ME004',
            'name': 'David Brown',
            'email': 'david.brown@university.edu',
            'courses': ['Mechanical Engineering', 'Thermodynamics', 'Mathematics'],
            'grades': [79, 86, 84]
        },
        {
            'roll_no': 'CS005',
            'name': 'Emma Davis',
            'email': 'emma.davis@university.edu',
            'courses': ['Computer Science', 'Artificial Intelligence', 'Data Structures'],
            'grades': [96, 92, 94]
        },
        {
            'roll_no': 'BIO006',
            'name': 'Frank Miller',
            'email': 'frank.miller@university.edu',
            'courses': ['Biology', 'Chemistry', 'Biochemistry'],
            'grades': [73, 81, 76]
        },
        {
            'roll_no': 'CHEM007',
            'name': 'Grace Wilson',
            'email': 'grace.wilson@university.edu',
            'courses': ['Chemistry', 'Organic Chemistry', 'Physical Chemistry'],
            'grades': [85, 91, 89]
        },
        {
            'roll_no': 'MATH008',
            'name': 'Henry Moore',
            'email': 'henry.moore@university.edu',
            'courses': ['Mathematics', 'Calculus', 'Linear Algebra', 'Statistics'],
            'grades': [87, 93, 89, 88]
        },
        {
            'roll_no': 'PHY009',
            'name': 'Ivy Taylor',
            'email': 'ivy.taylor@university.edu',
            'courses': ['Physics', 'Quantum Mechanics', 'Thermodynamics'],
            'grades': [83, 91, 87]
        },
        {
            'roll_no': 'CS010',
            'name': 'Jack Anderson',
            'email': 'jack.anderson@university.edu',
            'courses': ['Computer Science', 'Software Engineering', 'Database Systems', 'Web Development'],
            'grades': [79, 92, 88, 85]
        }
    ]
    
    # Add students to the system
    print(f"📝 Adding {len(sample_students)} sample students...")
    added_count = 0
    failed_count = 0
    
    for student in sample_students:
        try:
            success = manager.add_student(student)
            if success:
                added_count += 1
                print(f"  ✅ Added: {student['name']} ({student['roll_no']})")
            else:
                failed_count += 1
                print(f"  ❌ Failed: {student['name']} ({student['roll_no']}) - Roll number may exist")
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error adding {student['name']}: {str(e)}")
    
    # Display results
    print("\n" + "=" * 60)
    print(f"✅ Database initialization completed!")
    print(f"📊 Results:")
    print(f"   • Successfully added: {added_count} students")
    if failed_count > 0:
        print(f"   • Failed to add: {failed_count} students")
    print(f"   • Total students in database: {len(manager.get_all_students())}")
    
    print(f"\n🚀 Database is ready! You can now run your application.")
    return True

def main():
    """Main function to run database initialization"""
    print("🎓 Student Record Management System - Database Initializer")
    print("This script will populate your database with sample student data.")
    print("=" * 70)
    
    # Check for command line arguments
    force_overwrite = len(sys.argv) > 1 and sys.argv[1] == '--force'
    
    try:
        # Initialize the database
        success = initialize_sample_data(force_overwrite)
        
        if success:
            print(f"\n✅ Initialization successful!")
            print(f"You can now:")
            print(f"  • Access the web interface at the URL shown above")
            print(f"  • Start adding your own student records")
        else:
            print(f"\n❌ Initialization was cancelled or failed.")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all required Python files are available.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please check the error message and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()