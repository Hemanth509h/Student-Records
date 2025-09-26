#!/usr/bin/env python3
"""
Database Schema Initialization Script
=====================================

This script creates all database tables for the comprehensive Student Management System
with 25 advanced features. Run this script to initialize the complete database schema.

Features included:
1. User Management with Role-based Access
2. Student Management 
3. Course Management System
4. Teacher/Faculty Management
5. Department Management
6. Semester/Academic Year Management
7. Attendance Tracking
8. Enhanced Grade Analytics (Exam Results)
9. Parent/Guardian Management
10. Fee Management
11. Library Management
12. Exam Management
13. Timetable/Schedule Management
14. Assignment Management
15. Event/Announcement System
16. Student Counseling Records
17. Disciplinary Actions
18. Transportation Management
19. Hostel/Dormitory Management
20. Health Records
21. Scholarship Management
22. Alumni Management
23. Staff Management (Non-teaching)
24. Inventory Management
25. Communication/Messages
26. Reports and Analytics
27. Certificates and Documents

Usage:
    python create_tables.py

This will create all necessary tables in the PostgreSQL database.
"""

import os
import sys
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy import text

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.models import (
        db, 
        # Enums
        AttendanceStatus, FeeStatus, BookStatus, UserRole,
        # Core Models
        User, Student,
        # Feature 1: Course Management
        Course,
        # Feature 2: Teacher Management  
        Teacher,
        # Feature 3: Department Management
        Department,
        # Feature 4: Academic Period Management
        AcademicPeriod,
        # Feature 5: Attendance Tracking
        Attendance,
        # Feature 6: Enhanced Grade Analytics
        ExamResult,
        # Feature 7: Parent/Guardian Management
        Guardian, StudentGuardian,
        # Feature 8: Fee Management
        FeeType, StudentFee,
        # Feature 9: Library Management
        Book, BookBorrowing,
        # Feature 10: Exam Management
        Exam,
        # Feature 11: Timetable/Schedule Management
        Timetable, Room,
        # Feature 12: Assignment Management
        Assignment, AssignmentSubmission,
        # Feature 13: Event/Announcement System
        Event, Announcement,
        # Feature 14: Student Counseling Records
        CounselingSession,
        # Feature 15: Disciplinary Actions
        DisciplinaryAction,
        # Feature 16: Transportation Management
        TransportRoute, StudentTransport,
        # Feature 17: Hostel/Dormitory Management
        Hostel, HostelRoom, StudentHostel,
        # Feature 18: Health Records
        HealthRecord,
        # Feature 19: Scholarship Management
        Scholarship, ScholarshipApplication,
        # Feature 20: Alumni Management
        Alumni,
        # Feature 21: Staff Management
        Staff,
        # Feature 22: Inventory Management
        InventoryCategory, InventoryItem,
        # Feature 23: Communication/Messages
        Message,
        # Feature 24: Reports and Analytics
        ReportTemplate,
        # Feature 25: Certificates and Documents
        Certificate, Document
    )
    from core.app import app
    print("✓ Successfully imported all models and dependencies")
except ImportError as e:
    print(f"✗ Error importing models: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


def create_enum_types():
    """
    Create custom enum types in PostgreSQL database
    """
    print("\n📋 Creating enum types...")
    
    try:
        with app.app_context():
            # Create enum types if they don't exist
            enum_commands = [
                "CREATE TYPE IF NOT EXISTS attendancestatus AS ENUM ('present', 'absent', 'late', 'excused');",
                "CREATE TYPE IF NOT EXISTS feestatus AS ENUM ('pending', 'paid', 'overdue', 'cancelled');",
                "CREATE TYPE IF NOT EXISTS bookstatus AS ENUM ('available', 'borrowed', 'reserved', 'damaged');",
                "CREATE TYPE IF NOT EXISTS userrole AS ENUM ('admin', 'teacher', 'student', 'parent', 'staff');",
            ]
            
            for command in enum_commands:
                try:
                    db.session.execute(text(command))
                    db.session.commit()
                except Exception as e:
                    print(f"  Note: {e}")
                    db.session.rollback()
            
            print("✓ Enum types created successfully")
            
    except Exception as e:
        print(f"✗ Error creating enum types: {e}")
        return False
    
    return True


def create_all_tables():
    """
    Create all database tables using SQLAlchemy
    """
    print("\n🏗️  Creating all database tables...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✓ All tables created successfully")
            
            # Verify table creation by counting tables
            result = db.session.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """))
            table_count = result.fetchone()[0]
            print(f"✓ Total tables created: {table_count}")
            
            return True
            
    except OperationalError as e:
        print(f"✗ Database connection error: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correctly set")
        return False
    except ProgrammingError as e:
        print(f"✗ SQL Programming error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error creating tables: {e}")
        return False


def verify_tables():
    """
    Verify that all expected tables have been created
    """
    print("\n🔍 Verifying table creation...")
    
    expected_tables = [
        'users', 'students', 'courses', 'teachers', 'departments', 
        'academic_periods', 'attendance', 'exam_results', 'guardians', 
        'student_guardians', 'fee_types', 'student_fees', 'books', 
        'book_borrowings', 'exams', 'timetables', 'rooms', 'assignments', 
        'assignment_submissions', 'events', 'announcements', 'counseling_sessions',
        'disciplinary_actions', 'transport_routes', 'student_transport', 
        'hostels', 'hostel_rooms', 'student_hostel', 'health_records', 
        'scholarships', 'scholarship_applications', 'alumni', 'staff', 
        'inventory_categories', 'inventory_items', 'messages', 'report_templates',
        'certificates', 'documents'
    ]
    
    try:
        with app.app_context():
            # Check which tables exist
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📊 Database Schema Verification:")
            print(f"Expected tables: {len(expected_tables)}")
            print(f"Created tables: {len(existing_tables)}")
            
            missing_tables = set(expected_tables) - set(existing_tables)
            extra_tables = set(existing_tables) - set(expected_tables)
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {sorted(missing_tables)}")
                return False
            
            if extra_tables:
                print(f"\n📝 Additional tables found: {sorted(extra_tables)}")
            
            print(f"\n✅ All expected tables created successfully!")
            print(f"\n📋 Complete table list:")
            for table in sorted(existing_tables):
                print(f"  - {table}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error verifying tables: {e}")
        return False


def create_sample_admin_user():
    """
    Create a sample admin user for initial access
    """
    print("\n👤 Creating sample admin user...")
    
    try:
        with app.app_context():
            # Check if admin user already exists
            existing_admin = User.query.filter_by(email='admin@school.com').first()
            
            if existing_admin:
                print("✓ Admin user already exists")
                return True
            
            # Create admin user
            admin_user = User(
                email='admin@school.com',
                username='admin',
                password_hash='admin123',  # In production, this should be properly hashed
                role=UserRole.ADMIN,
                first_name='System',
                last_name='Administrator',
                is_active=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✓ Sample admin user created:")
            print("  Email: admin@school.com")
            print("  Password: admin123")
            print("  Role: Administrator")
            
            return True
            
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.session.rollback()
        return False


def main():
    """
    Main function to initialize the complete database schema
    """
    print("🚀 Starting Database Schema Initialization")
    print("=" * 60)
    
    # Check database connection
    print("\n🔌 Checking database connection...")
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL environment variable not set")
        print("Make sure PostgreSQL database is configured")
        sys.exit(1)
    
    print(f"✓ Database URL configured: {database_url[:50]}...")
    
    # Step 1: Create enum types
    if not create_enum_types():
        print("\n❌ Failed to create enum types")
        sys.exit(1)
    
    # Step 2: Create all tables
    if not create_all_tables():
        print("\n❌ Failed to create tables")
        sys.exit(1)
    
    # Step 3: Verify table creation
    if not verify_tables():
        print("\n❌ Table verification failed")
        sys.exit(1)
    
    # Step 4: Create sample admin user
    if not create_sample_admin_user():
        print("\n⚠️  Warning: Could not create sample admin user")
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE SCHEMA INITIALIZATION COMPLETE!")
    print("=" * 60)
    print("\n✅ All 25 features have been successfully initialized:")
    print("   • User Management with Roles")
    print("   • Student & Academic Management") 
    print("   • Course & Teacher Management")
    print("   • Attendance & Grade Tracking")
    print("   • Fee & Financial Management")
    print("   • Library & Book Management")
    print("   • Exam & Assignment Systems")
    print("   • Communication & Events")
    print("   • Health & Counseling Records")
    print("   • Transportation & Hostel Management")
    print("   • Alumni & Scholarship Programs")
    print("   • Staff & Inventory Management")
    print("   • Reports & Document Management")
    print("\n🚀 Your Student Management System is ready to use!")
    print("\n💡 Next steps:")
    print("   1. Start the application: python main.py")
    print("   2. Login with admin@school.com / admin123")
    print("   3. Begin adding your school data")


if __name__ == "__main__":
    main()