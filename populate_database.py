#!/usr/bin/env python3
"""
Database Population Script
Populates the database with up to 1000 students if the database is not already populated.
Creates tables if they don't exist.
"""

import os
import random
from core.app import app, db
from models import Student

# Sample data for generating realistic student records
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Helen", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Dorothy", "Mark", "Lisa", "Donald", "Anna",
    "Steven", "Kimberly", "Paul", "Deborah", "Andrew", "Laura", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amy", "Brian", "Angela", "George", "Brenda",
    "Timothy", "Emma", "Ronald", "Olivia", "Jason", "Sophia", "Edward", "Cynthia",
    "Jeffrey", "Marie", "Ryan", "Janet", "Jacob", "Catherine", "Gary", "Frances",
    "Nicholas", "Christine", "Eric", "Sharon", "Jonathan", "Debra", "Stephen", "Rachel",
    "Larry", "Carolyn", "Justin", "Janet", "Scott", "Virginia", "Brandon", "Maria",
    "Benjamin", "Heather", "Samuel", "Diane", "Gregory", "Ruth", "Alexander", "Julie",
    "Patrick", "Joyce", "Frank", "Victoria", "Raymond", "Kelly", "Jack", "Christina"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "Bennett", "Gray", "Mendoza", "Ruiz",
    "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long"
]

COURSES = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "English Literature",
    "History", "Geography", "Psychology", "Philosophy", "Economics", "Business Studies",
    "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Chemical Engineering",
    "Data Science", "Statistics", "Calculus", "Linear Algebra", "Organic Chemistry", "Genetics",
    "Molecular Biology", "Environmental Science", "Political Science", "Sociology", "Anthropology",
    "Art History", "Music Theory", "Creative Writing", "Foreign Languages", "Marketing",
    "Finance", "Accounting", "Operations Research", "Database Systems", "Software Engineering",
    "Web Development", "Machine Learning", "Artificial Intelligence", "Network Security"
]

def generate_student_data():
    """Generate realistic student data"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    
    # Generate roll number (format: 2024001 to 2024999)
    roll_no = f"2024{random.randint(1, 999):03d}"
    
    # Generate email
    email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
    
    # Generate 3-6 random courses
    num_courses = random.randint(3, 6)
    selected_courses = random.sample(COURSES, num_courses)
    
    # Generate grades for each course (60-100)
    grades = [round(random.uniform(60.0, 100.0), 2) for _ in range(num_courses)]
    
    return {
        'roll_no': roll_no,
        'name': name,
        'email': email,
        'courses': selected_courses,
        'grades': grades
    }

def populate_database():
    """Main function to populate the database with 1000 students"""
    with app.app_context():
        try:
            # Create tables if they don't exist
            print("Creating database tables if they don't exist...")
            db.create_all()
            print("✓ Database tables ready")
            
            # Check if database is already populated
            existing_count = Student.query.count()
            print(f"Current students in database: {existing_count}")
            
            if existing_count >= 1000:
                print("Database already has 1000 or more students. No action needed.")
                return
            
            students_to_create = 1000 - existing_count
            print(f"Will create {students_to_create} new students...")
            
            # Get existing roll numbers to avoid duplicates
            existing_roll_nos = set(student.roll_no for student in Student.query.with_entities(Student.roll_no).all())
            
            created_count = 0
            attempts = 0
            max_attempts = students_to_create * 2  # Allow some attempts for duplicate roll numbers
            
            while created_count < students_to_create and attempts < max_attempts:
                attempts += 1
                
                try:
                    student_data = generate_student_data()
                    
                    # Skip if roll number already exists
                    if student_data['roll_no'] in existing_roll_nos:
                        continue
                    
                    # Create new student
                    student = Student()
                    student.roll_no = student_data['roll_no']
                    student.name = student_data['name']
                    student.email = student_data['email']
                    student.courses = student_data['courses']
                    student.grades = student_data['grades']
                    
                    db.session.add(student)
                    existing_roll_nos.add(student_data['roll_no'])
                    created_count += 1
                    
                    # Commit in batches of 50 for better performance
                    if created_count % 50 == 0:
                        db.session.commit()
                        print(f"✓ Created {created_count} students...")
                        
                except Exception as e:
                    print(f"Error creating student: {e}")
                    db.session.rollback()
                    continue
            
            # Final commit
            db.session.commit()
            print(f"✓ Successfully created {created_count} students")
            print(f"✓ Total students in database: {Student.query.count()}")
            
        except Exception as e:
            print(f"Error populating database: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("Starting database population...")
    populate_database()
    print("Database population completed!")