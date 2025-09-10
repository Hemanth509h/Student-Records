import os
import random
from flask import Flask
from models import db, Student

# Flask app setup for SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/student_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Sample data for generating students
first_names = [
    "John", "Jane", "Mike", "Sarah", "David", "Emily", "Robert", "Lisa", 
    "James", "Mary", "William", "Patricia", "Richard", "Jennifer", "Charles",
    "Linda", "Joseph", "Elizabeth", "Thomas", "Barbara", "Christopher", "Susan",
    "Daniel", "Jessica", "Matthew", "Karen", "Anthony", "Nancy", "Mark", "Helen",
    "Donald", "Sandra", "Steven", "Donna", "Paul", "Carol", "Andrew", "Ruth",
    "Kenneth", "Sharon", "Ryan", "Michelle", "Jacob", "Laura", "Nicholas", "Sarah",
    "Gary", "Kimberly", "Timothy", "Deborah", "Jose", "Dorothy", "Larry", "Amy",
    "Jeffrey", "Angela", "Frank", "Ashley", "Scott", "Brenda", "Eric", "Emma"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
]

courses = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
    "English Literature", "History", "Geography", "Economics", "Psychology",
    "Sociology", "Philosophy", "Art", "Music", "Physical Education",
    "Statistics", "Calculus", "Linear Algebra", "Data Structures", "Algorithms",
    "Database Systems", "Web Development", "Machine Learning", "Artificial Intelligence",
    "Software Engineering", "Network Security", "Operating Systems", "Digital Logic"
]

def generate_student_data():
    """Generate random student data"""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"
    
    # Generate roll number
    roll_no = f"ST{random.randint(1000, 9999)}"
    
    # Generate email
    email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
    
    # Generate random courses (3-6 courses per student)
    num_courses = random.randint(3, 6)
    student_courses = random.sample(courses, num_courses)
    
    # Generate grades (60-100)
    grades = [round(random.uniform(60, 100), 1) for _ in range(num_courses)]
    
    return {
        'roll_no': roll_no,
        'name': name,
        'email': email,
        'courses': student_courses,
        'grades': grades
    }

def populate_database():
    """Create database tables and add 500 students using SQLAlchemy"""
    print("Starting SQLAlchemy database setup and population...")
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Check existing data
            existing_count = Student.query.count()
            print(f"Found {existing_count} existing students")
            
            if existing_count > 0:
                response = input("Clear existing data? (y/n): ").lower()
                if response == 'y':
                    Student.query.delete()
                    db.session.commit()
                    print("Cleared existing student data")
            
            print("Adding 500 students using SQLAlchemy...")
            added = 0
            attempts = 0
            
            while added < 500 and attempts < 1000:  # Prevent infinite loop
                attempts += 1
                student_data = generate_student_data()
                
                # Check if roll number already exists
                if Student.query.filter_by(roll_no=student_data['roll_no']).first():
                    continue
                
                try:
                    # Create new student using SQLAlchemy model
                    new_student = Student(
                        roll_no=student_data['roll_no'],
                        name=student_data['name'],
                        email=student_data['email'],
                        courses=student_data['courses'],
                        grades=student_data['grades']
                    )
                    
                    db.session.add(new_student)
                    db.session.commit()
                    added += 1
                    
                    if added % 50 == 0:
                        print(f"Added {added} students...")
                        
                except Exception as e:
                    print(f"Error adding student {student_data['name']}: {e}")
                    db.session.rollback()
                    continue
            
            print(f"Successfully added {added} students using SQLAlchemy!")
            print("Database setup and population completed!")
            
        except Exception as e:
            print(f"Error during population: {e}")
            db.session.rollback()

if __name__ == '__main__':
    populate_database()