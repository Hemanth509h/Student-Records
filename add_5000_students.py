#!/usr/bin/env python3
# Shebang line - tells system to run this script using python3

"""
Script to populate the database with users and 5000+ students
This script generates sample data for testing and demonstration purposes
"""

# Import os module for file path operations
import os
# Import sys module for system-level operations and path manipulation
import sys
# Import random module for generating random data
import random
# Import datetime for timestamp creation
from datetime import datetime
# Import password hashing function from Werkzeug security library
from werkzeug.security import generate_password_hash

# Add current directory to Python path so we can import our modules
# os.path.dirname gets the directory containing this script
# os.path.abspath gets the absolute path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database instance and model classes from our application
from core.models import db, Student, User
# Import Flask app instance to use application context
from core.app import app

# Sample data lists for generating realistic student records
# List of common first names to randomly assign to generated students
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

# List of common last names to randomly assign to generated students
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

# List of course names that students can be enrolled in
courses_list = [
    "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science",
    "English Literature", "History", "Geography", "Economics", "Business Studies",
    "Psychology", "Sociology", "Political Science", "Philosophy", "Art",
    "Music", "Physical Education", "Spanish", "French", "German",
    "Statistics", "Calculus", "Linear Algebra", "Organic Chemistry", "Environmental Science",
    "Data Science", "Web Development", "Machine Learning", "Cybersecurity", "Database Systems"
]

# Function to generate random student data for a given index number
def generate_student_data(index):
    """Generate random student data"""
    # Create roll number with STU prefix and 5-digit zero-padded index
    # Example: index 1 becomes "STU00001", index 100 becomes "STU00100"
    roll_no = f"STU{index:05d}"
    # Randomly select a first name from the list
    first_name = random.choice(first_names)
    # Randomly select a last name from the list
    last_name = random.choice(last_names)
    # Combine first and last name to create full name
    name = f"{first_name} {last_name}"
    # Generate email address using lowercase name and index
    # Example: "john.smith123@university.edu"
    email = f"{first_name.lower()}.{last_name.lower()}{index}@university.edu"
    
    # Randomly determine number of courses for this student (between 3 and 6)
    num_courses = random.randint(3, 6)
    # Randomly select that many courses from the courses_list (no duplicates)
    # random.sample ensures each course is selected only once
    courses = random.sample(courses_list, num_courses)
    
    # Generate random grades for each course
    # Each grade is a random float between 60 and 100, rounded to 1 decimal place
    # List comprehension creates a grade for each course
    grades = [round(random.uniform(60, 100), 1) for _ in range(num_courses)]
    
    # Return dictionary containing all student data
    return {
        'roll_no': roll_no,  # Student's roll number
        'name': name,  # Student's full name
        'email': email,  # Student's email address
        'courses': courses,  # List of enrolled courses
        'grades': grades  # List of grades (corresponding to courses)
    }

# Function to add sample user accounts to the database
def add_users():
    """Add sample users to the database"""
    # Print header for this section of output
    print(f"\n{'='*60}")  # Print separator line
    print(f"Adding sample users to the database...")  # Print action description
    print(f"{'='*60}\n")  # Print separator line
    
    # List of sample users to create (admin, teachers, staff, parent)
    # Each dictionary contains all the information for one user account
    sample_users = [
        {  # Admin user with full system access
            'email': 'admin@school.com',  # Login email
            'username': 'admin',  # Username
            'password': 'admin123',  # Plain text password (will be hashed)
            'role': 'admin',  # User role
            'first_name': 'Admin',  # First name
            'last_name': 'User',  # Last name
            'phone': '+1-555-0001',  # Phone number
            'active': True  # Account is active
        },
        {  # First teacher account
            'email': 'teacher1@school.com',
            'username': 'teacher1',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'John',
            'last_name': 'Smith',
            'phone': '+1-555-0002',
            'active': True
        },
        {  # Second teacher account
            'email': 'teacher2@school.com',
            'username': 'teacher2',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'phone': '+1-555-0003',
            'active': True
        },
        {  # Staff member account
            'email': 'staff@school.com',
            'username': 'staff',
            'password': 'staff123',
            'role': 'staff',
            'first_name': 'David',
            'last_name': 'Williams',
            'phone': '+1-555-0004',
            'active': True
        },
        {  # Parent account
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
    
    # Counter to track how many new users were added
    added_count = 0
    # Loop through each user dictionary in the sample_users list
    for user_data in sample_users:
        # Check if a user with this email already exists in database
        existing_user = User.query.filter_by(email=user_data['email']).first()
        # Only add user if they don't already exist (avoid duplicates)
        if not existing_user:
            # Create a new User object with all the user data
            user = User(
                email=user_data['email'],  # Set email
                username=user_data['username'],  # Set username
                password_hash=generate_password_hash(user_data['password']),  # Hash the password for security
                role=user_data['role'],  # Set user role
                first_name=user_data['first_name'],  # Set first name
                last_name=user_data['last_name'],  # Set last name
                phone=user_data['phone'],  # Set phone number
                active=user_data['active'],  # Set active status
                created_at=datetime.utcnow()  # Set creation timestamp
            )
            # Add user to database session (not yet saved)
            db.session.add(user)
            # Increment counter
            added_count += 1
            # Print success message with checkmark emoji
            print(f"✅ Added user: {user_data['email']} ({user_data['role']})")
        # If user already exists
        else:
            # Print warning message with warning emoji
            print(f"⚠️  User already exists: {user_data['email']}")
    
    # Try to save all users to database
    try:
        # Commit the database transaction (save all changes)
        db.session.commit()
        # Print success summary
        print(f"\n✅ Successfully added {added_count} users!")
        # Return True to indicate success
        return True
    # If database commit fails
    except Exception as e:
        # Rollback the transaction (undo all changes)
        db.session.rollback()
        # Print error message
        print(f"❌ Error adding users: {e}")
        # Return False to indicate failure
        return False

# Function to add students to database in batches for efficiency
# num_students: total number of students to generate (default 5000)
# batch_size: how many students to add at once (default 100)
def add_students(num_students=5000, batch_size=100):
    """Add students to the database in batches"""
    # Print header for this section
    print(f"\n{'='*60}")  # Print separator line
    print(f"Adding {num_students} students to the database...")  # Show total to add
    print(f"{'='*60}\n")  # Print separator line
    
    # Counter to track total number of students added
    total_added = 0
    
    # Loop through students in batches (0 to num_students, incrementing by batch_size)
    # This prevents memory issues by processing students in smaller groups
    for batch_start in range(0, num_students, batch_size):
        # Calculate where this batch ends (don't exceed total number)
        # min() ensures we don't go past the last student
        batch_end = min(batch_start + batch_size, num_students)
        # Create empty list to store this batch of students
        batch_students = []
        
        # Loop through each student number in this batch
        for i in range(batch_start, batch_end):
            # Generate random data for this student (i+1 because roll numbers start at 1)
            student_data = generate_student_data(i + 1)
            # Create a Student object from the generated data
            student = Student(
                roll_no=student_data['roll_no'],  # Set roll number
                name=student_data['name'],  # Set name
                email=student_data['email'],  # Set email
                courses=student_data['courses'],  # Set courses list
                grades=student_data['grades']  # Set grades list
            )
            # Add this student to the current batch list
            batch_students.append(student)
        
        # Try to save this batch to the database
        try:
            # Bulk save all students in this batch (faster than one-by-one)
            db.session.bulk_save_objects(batch_students)
            # Commit the transaction to save to database
            db.session.commit()
            # Update total count with students from this batch
            total_added += len(batch_students)
            # Print progress update showing batch number and progress
            # batch_start//batch_size + 1 gives current batch number
            # (num_students-1)//batch_size + 1 gives total batches
            print(f"✅ Added batch {batch_start//batch_size + 1}/{(num_students-1)//batch_size + 1} - Total students: {total_added}")
        # If saving batch fails
        except Exception as e:
            # Rollback the transaction to undo partial changes
            db.session.rollback()
            # Print error message
            print(f"❌ Error adding batch: {e}")
            # Return False to indicate failure
            return False
    
    # Print final summary header
    print(f"\n{'='*60}")  # Print separator
    print(f"✅ Successfully added {total_added} students!")  # Show total added
    print(f"{'='*60}\n")  # Print separator
    
    # Query database to show final statistics
    # Get all students from database
    all_students = Student.query.all()
    # Print total count in database (may include previously existing students)
    print(f"Total students in database: {len(all_students)}")
    
    # Return True to indicate success
    return True

# Main function to populate database with both users and students
# num_students: number of student records to generate (default 5000)
def populate_database(num_students=5000):
    """Populate database with users and students"""
    # Create Flask application context (required for database operations)
    # This ensures we can access the database and models
    with app.app_context():
        # Print main script header
        print(f"\n{'#'*60}")  # Print header border
        print(f"# DATABASE POPULATION SCRIPT")  # Print script title
        print(f"{'#'*60}\n")  # Print header border
        
        # Step 1: Add user accounts first (admin, teachers, staff, parent)
        # Call add_users function and store result
        users_success = add_users()
        # Check if user creation failed
        if not users_success:
            # Print error message
            print("\n❌ Failed to add users. Aborting...")
            # Return False to indicate failure and stop execution
            return False
        
        # Step 2: Add student records (only if users were added successfully)
        # Call add_students function with specified number and store result
        students_success = add_students(num_students)
        # Check if student creation failed
        if not students_success:
            # Print error message
            print("\n❌ Failed to add students. Aborting...")
            # Return False to indicate failure
            return False
        
        # Step 3: Show final summary statistics
        # Count total users in database (query the database)
        total_users = User.query.count()
        # Count total students in database (query the database)
        total_students = Student.query.count()
        
        # Print completion banner
        print(f"\n{'#'*60}")  # Print border
        print(f"# POPULATION COMPLETE!")  # Print completion message
        print(f"{'#'*60}")  # Print border
        print(f"Total Users: {total_users}")  # Show total user count
        print(f"Total Students: {total_students}")  # Show total student count
        print(f"{'#'*60}\n")  # Print border
        
        # Print login credentials for testing
        print("\n📝 Sample Login Credentials:")  # Print credentials header
        print(f"  Admin:   admin@school.com / admin123")  # Admin credentials
        print(f"  Teacher: teacher1@school.com / teacher123")  # Teacher credentials
        print(f"  Staff:   staff@school.com / staff123")  # Staff credentials
        print(f"  Parent:  parent1@example.com / parent123\n")  # Parent credentials
        
        # Return True to indicate successful completion
        return True

# Check if this script is being run directly (not imported as a module)
if __name__ == "__main__":
    # Call the populate_database function with 5000 students
    success = populate_database(5000)
    # Exit the script with appropriate exit code
    # Exit code 0 indicates success, 1 indicates failure
    # 'if success' evaluates to True or False, which becomes 0 or 1
    sys.exit(0 if success else 1)
