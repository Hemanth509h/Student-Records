#!/usr/bin/env python3
"""
Script to add 5000 sample students to the database
"""

import os
import sys
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import db, Student
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

def add_students(num_students=5000, batch_size=100):
    """Add students to the database in batches"""
    with app.app_context():
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

if __name__ == "__main__":
    success = add_students(5000)
    sys.exit(0 if success else 1)
