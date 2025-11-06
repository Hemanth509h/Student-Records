#!/usr/bin/env python3
"""
Script to populate the database with users and 5000+ students
"""

import os
import sys
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import db, Student, User
from core.app import app

# Sample data for generating students
first_names = [
    "Alexander", "Emma", "Michael", "Olivia", "James", "Sophia", "William", "Isabella", 
    "Benjamin", "Mia", "Lucas", "Charlotte", "Henry", "Amelia", "Theodore", "Harper",
    "Jack", "Evelyn", "Owen", "Abigail", "Sebastian", "Emily", "Aiden", "Elizabeth",
    "Matthew", "Sofia", "Samuel", "Avery", "David", "Ella", "Joseph", "Scarlett",
    "Carter", "Grace", "Wyatt", "Chloe", "John", "Victoria", "Luke", "Riley",
    "Jayden", "Aria", "Dylan", "Lily", "Grayson", "Aubrey", "Levi", "Zoey",
    "Isaac", "Penelope", "Gabriel", "Lillian", "Julian", "Addison", "Mateo", "Layla",
    "Anthony", "Natalie", "Jaxon", "Camila", "Lincoln", "Hannah", "Joshua", "Brooklyn",
    "Christopher", "Zoe", "Andrew", "Nora", "Theodore", "Leah", "Caleb", "Savannah",
    "Ryan", "Audrey", "Asher", "Claire", "Nathan", "Eleanor", "Thomas", "Skylar",
    "Leo", "Ellie", "Isaiah", "Samantha", "Charles", "Stella", "Josiah", "Paisley",
    "Hudson", "Violet", "Christian", "Aurora", "Hunter", "Lucy", "Connor", "Anna",
    "Eli", "Caroline", "Ezra", "Genesis", "Aaron", "Aaliyah", "Landon", "Kennedy"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen",
    "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter",
    "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz",
    "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", "Cook",
    "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", "Reed",
    "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz",
    "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long"
]

courses_list = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science",
    "English Literature", "History", "Geography", "Economics", "Business Studies",
    "Psychology", "Sociology", "Political Science", "Philosophy", "Art",
    "Music", "Physical Education", "Spanish", "French", "German",
    "Statistics", "Calculus", "Linear Algebra", "Organic Chemistry", "Environmental Science",
    "Data Science", "Web Development", "Machine Learning", "Cybersecurity", "Database Systems"
]

def generate_student_data(index):
    """Generate random student data"""
    roll_no = f"STU{index:05d}"
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{index}@university.edu"
    
    # Random number of courses (3-6)
    num_courses = random.randint(3, 6)
    courses = random.sample(courses_list, num_courses)
    
    # Generate grades for each course (60-100)
    grades = [round(random.uniform(60, 100), 1) for _ in range(num_courses)]
    
    return {
        'roll_no': roll_no,
        'name': name,
        'email': email,
        'courses': courses,
        'grades': grades
    }

def add_users():
    """Add sample users to the database"""
    print(f"\n{'='*60}")
    print(f"Adding sample users to the database...")
    print(f"{'='*60}\n")
    
    sample_users = [
        {
            'email': 'admin@school.com',
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'phone': '+1-555-0001',
            'active': True
        },
        {
            'email': 'teacher1@school.com',
            'username': 'teacher1',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'John',
            'last_name': 'Smith',
            'phone': '+1-555-0002',
            'active': True
        },
        {
            'email': 'teacher2@school.com',
            'username': 'teacher2',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'phone': '+1-555-0003',
            'active': True
        },
        {
            'email': 'staff@school.com',
            'username': 'staff',
            'password': 'staff123',
            'role': 'staff',
            'first_name': 'David',
            'last_name': 'Williams',
            'phone': '+1-555-0004',
            'active': True
        },
        {
            'email': 'parent1@example.com',
            'username': 'parent1',
            'password': 'parent123',
            'role': 'parent',
            'first_name': 'Emily',
            'last_name': 'Brown',
            'phone': '+1-555-0005',
            'active': True
        }
    ]
    
    added_count = 0
    for user_data in sample_users:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                active=user_data['active'],
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            added_count += 1
            print(f"✅ Added user: {user_data['email']} ({user_data['role']})")
        else:
            print(f"⚠️  User already exists: {user_data['email']}")
    
    try:
        db.session.commit()
        print(f"\n✅ Successfully added {added_count} users!")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding users: {e}")
        return False

def add_students(num_students=5000, batch_size=100):
    """Add students to the database in batches"""
    print(f"\n{'='*60}")
    print(f"Adding {num_students} students to the database...")
    print(f"{'='*60}\n")
    
    total_added = 0
    
    for batch_start in range(0, num_students, batch_size):
        batch_end = min(batch_start + batch_size, num_students)
        batch_students = []
        
        for i in range(batch_start, batch_end):
            student_data = generate_student_data(i + 1)
            student = Student(
                roll_no=student_data['roll_no'],
                name=student_data['name'],
                email=student_data['email'],
                courses=student_data['courses'],
                grades=student_data['grades']
            )
            batch_students.append(student)
        
        try:
            db.session.bulk_save_objects(batch_students)
            db.session.commit()
            total_added += len(batch_students)
            print(f"✅ Added batch {batch_start//batch_size + 1}/{(num_students-1)//batch_size + 1} - Total students: {total_added}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding batch: {e}")
            return False
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully added {total_added} students!")
    print(f"{'='*60}\n")
    
    # Show some statistics
    all_students = Student.query.all()
    print(f"Total students in database: {len(all_students)}")
    
    return True

def populate_database(num_students=5000):
    """Populate database with users and students"""
    with app.app_context():
        print(f"\n{'#'*60}")
        print(f"# DATABASE POPULATION SCRIPT")
        print(f"{'#'*60}\n")
        
        # Add users first
        users_success = add_users()
        if not users_success:
            print("\n❌ Failed to add users. Aborting...")
            return False
        
        # Then add students
        students_success = add_students(num_students)
        if not students_success:
            print("\n❌ Failed to add students. Aborting...")
            return False
        
        # Final summary
        total_users = User.query.count()
        total_students = Student.query.count()
        
        print(f"\n{'#'*60}")
        print(f"# POPULATION COMPLETE!")
        print(f"{'#'*60}")
        print(f"Total Users: {total_users}")
        print(f"Total Students: {total_students}")
        print(f"{'#'*60}\n")
        
        print("\n📝 Sample Login Credentials:")
        print(f"  Admin:   admin@school.com / admin123")
        print(f"  Teacher: teacher1@school.com / teacher123")
        print(f"  Staff:   staff@school.com / staff123")
        print(f"  Parent:  parent1@example.com / parent123\n")
        
        return True

if __name__ == "__main__":
    success = populate_database(5000)
    sys.exit(0 if success else 1)
