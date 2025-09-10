import os
import psycopg2
import random

# Database connection for server (without specific database)
def get_server_connection():
    return psycopg2.connect("postgresql://postgres:12345678@localhost:5432/")

# Database connection for specific database
def get_db_connection():
    return psycopg2.connect("postgresql://postgres:12345678@localhost:5432/student_management")

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

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    print("Checking if database exists...")
    try:
        # Connect to PostgreSQL server (default database)
        conn = get_server_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'student_management'")
        if cur.fetchone():
            print("Database 'student_management' already exists")
        else:
            # Create database
            cur.execute("CREATE DATABASE student_management")
            print("Created database 'student_management'")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def create_table_if_not_exists():
    """Create students table if it doesn't exist"""
    print("Checking if students table exists...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'students'
            )
        """)
        
        result = cur.fetchone()
        if result and result[0]:
            print("Students table already exists")
        else:
            # Create table
            cur.execute("""
                CREATE TABLE students (
                    id SERIAL PRIMARY KEY,
                    roll_no VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    courses TEXT[] NOT NULL,
                    grades NUMERIC[] NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Created students table")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

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
    """Create database, table and add 500 students"""
    print("Starting database setup and population...")
    
    # Step 1: Create database if not exists
    if not create_database_if_not_exists():
        print("Failed to create/connect to database")
        return
    
    # Step 2: Create table if not exists
    if not create_table_if_not_exists():
        print("Failed to create students table")
        return
    
    # Step 3: Populate data
    print("Connecting to student_management database...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check existing data
        cur.execute("SELECT COUNT(*) FROM students")
        result = cur.fetchone()
        existing_count = result[0] if result else 0
        print(f"Found {existing_count} existing students")
        
        if existing_count > 0:
            response = input("Clear existing data? (y/n): ").lower()
            if response == 'y':
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
        print("Database setup and population completed!")
        
    except Exception as e:
        print(f"Error during population: {e}")

if __name__ == '__main__':
    populate_database()