import os
import psycopg2
import random

# Database connection
def get_db():
    return psycopg2.connect(os.environ['DATABASE_URL'])

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
    """Add 500 students to the database"""
    print("Connecting to database...")
    conn = get_db()
    cur = conn.cursor()
    
    # Clear existing data
    cur.execute("DELETE FROM students")
    conn.commit()
    print("Cleared existing student data")
    
    print("Adding 500 students...")
    added = 0
    attempts = 0
    
    while added < 500 and attempts < 1000:  # Prevent infinite loop
        attempts += 1
        student = generate_student_data()
        
        try:
            cur.execute(
                "INSERT INTO students (roll_no, name, email, courses, grades) VALUES (%s, %s, %s, %s, %s)",
                (student['roll_no'], student['name'], student['email'], student['courses'], student['grades'])
            )
            conn.commit()
            added += 1
            
            if added % 50 == 0:
                print(f"Added {added} students...")
                
        except psycopg2.IntegrityError:
            # Roll number already exists, try again
            conn.rollback()
            continue
    
    cur.close()
    conn.close()
    print(f"Successfully added {added} students to the database!")

if __name__ == '__main__':
    populate_database()