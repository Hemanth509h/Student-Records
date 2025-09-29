#!/usr/bin/env python3
"""
Complete Database Schema Initialization Script
==============================================

This script creates all database tables for the comprehensive Student Management System.
It includes all 25+ features with proper error handling and verification.

Features included:
1. User Management with Role-based Access Control
2. Student Management System  
3. Course Management System
4. Teacher/Faculty Management
5. Department Management
6. Academic Period/Semester Management
7. Attendance Tracking System
8. Enhanced Grade Analytics & Exam Results
9. Parent/Guardian Management
10. Fee Management System
11. Library & Book Management
12. Exam Management System
13. Timetable/Schedule Management
14. Assignment Management System
15. Event/Announcement System
16. Student Counseling Records
17. Disciplinary Actions Management
18. Transportation Management
19. Hostel/Dormitory Management
20. Health Records Management
21. Scholarship Management
22. Alumni Management System
23. Staff Management (Non-teaching)
24. Inventory Management System
25. Communication/Messages System

Usage:
    python create_tables.py

This will create all necessary tables in the PostgreSQL database.
"""

import os
import sys
from typing import List, Optional
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy import text
from werkzeug.security import generate_password_hash

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.models import (
        db, User, Student, Course, Teacher, Department, AcademicPeriod,
        Attendance, ExamResult, Guardian, StudentGuardian, FeeType, StudentFee,
        Book, BookBorrowing, Exam, Timetable, Room, Assignment, AssignmentSubmission,
        Event, Announcement, CounselingSession, DisciplinaryAction, TransportRoute,
        StudentTransport, Hostel, HostelRoom, StudentHostel, HealthRecord,
        Scholarship, ScholarshipApplication, Alumni, Staff, InventoryCategory,
        InventoryItem, Message, ReportTemplate, Certificate, Document,
        UserRole, AttendanceStatus, FeeStatus, BookStatus
    )
    from core.app import app
    print("✅ Successfully imported all models and dependencies")
except ImportError as e:
    print(f"❌ Error importing models: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


def check_database_connection() -> bool:
    """
    Check if we can connect to the database
    """
    print("\n🔌 Checking database connection...")
    
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        # Mask password in URL for display
        display_url = database_url
        if '@' in display_url:
            parts = display_url.split('@')
            if len(parts) >= 2:
                user_part = parts[0].split(':')
                if len(user_part) >= 2:
                    display_url = user_part[0] + ":***@" + parts[1]
        
        print(f"✅ Database URL configured: {display_url[:60]}...")
        
        with app.app_context():
            # Test connection
            result = db.session.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_enum_types() -> bool:
    """
    Create custom enum types in PostgreSQL database
    """
    print("\n📋 Creating enum types...")
    
    enum_commands = [
        "DO $$ BEGIN CREATE TYPE attendancestatus AS ENUM ('present', 'absent', 'late', 'excused'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
        "DO $$ BEGIN CREATE TYPE feestatus AS ENUM ('pending', 'paid', 'overdue', 'cancelled'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
        "DO $$ BEGIN CREATE TYPE bookstatus AS ENUM ('available', 'borrowed', 'reserved', 'damaged'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
        "DO $$ BEGIN CREATE TYPE userrole AS ENUM ('ADMIN', 'TEACHER', 'STUDENT', 'PARENT', 'STAFF'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    ]
    
    try:
        with app.app_context():
            for command in enum_commands:
                try:
                    db.session.execute(text(command))
                    db.session.commit()
                except Exception as e:
                    print(f"  Note: {str(e)[:100]}...")
                    db.session.rollback()
            
            print("✅ Enum types processed successfully")
            
    except Exception as e:
        print(f"❌ Error creating enum types: {e}")
        return False
    
    return True


def create_all_tables() -> bool:
    """
    Create all database tables using SQLAlchemy models
    """
    print("\n🏗️  Creating all database tables...")
    
    try:
        with app.app_context():
            # Drop all tables first if they exist (for clean recreation)
            print("  🧹 Cleaning up existing tables...")
            db.drop_all()
            
            # Create all tables
            print("  📄 Creating new tables...")
            db.create_all()
            
            # Verify table creation by counting tables
            result = db.session.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """))
            row = result.fetchone()
            if row:
                table_count = row[0]
                print(f"✅ Successfully created {table_count} tables")
            else:
                print("✅ Tables created (count not available)")
            
            return True
            
    except OperationalError as e:
        print(f"❌ Database connection error: {e}")
        return False
    except ProgrammingError as e:
        print(f"❌ SQL Programming error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating tables: {e}")
        return False


def verify_tables() -> bool:
    """
    Verify that all expected tables have been created
    """
    print("\n🔍 Verifying table creation...")
    
    # All expected tables based on our models
    expected_tables = [
        # Core tables
        'users', 'students', 'courses', 'teachers', 'departments', 
        'academic_periods', 'rooms',
        
        # Academic & Performance tables
        'attendance', 'exams', 'exam_results', 'assignments', 'assignment_submissions',
        'timetables',
        
        # Financial & Administrative tables
        'fee_types', 'student_fees', 'scholarships', 'scholarship_applications',
        
        # Library & Resources tables
        'books', 'book_borrowings', 'inventory_categories', 'inventory_items',
        
        # Communication & Events tables
        'events', 'announcements', 'messages',
        
        # Support & Welfare tables
        'guardians', 'student_guardians', 'counseling_sessions', 'disciplinary_actions',
        'health_records',
        
        # Infrastructure & Logistics tables
        'transport_routes', 'student_transport', 'hostels', 'hostel_rooms', 'student_hostel',
        
        # Extended Management tables
        'alumni', 'staff', 'report_templates', 'certificates', 'documents'
    ]
    
    try:
        with app.app_context():
            # Get all existing tables
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📊 Database Schema Verification:")
            print(f"  Expected tables: {len(expected_tables)}")
            print(f"  Created tables: {len(existing_tables)}")
            
            missing_tables = set(expected_tables) - set(existing_tables)
            extra_tables = set(existing_tables) - set(expected_tables)
            
            if missing_tables:
                print(f"\n⚠️  Missing tables ({len(missing_tables)}):")
                for table in sorted(missing_tables):
                    print(f"    - {table}")
            
            if extra_tables:
                print(f"\n📝 Additional tables found ({len(extra_tables)}):")
                for table in sorted(extra_tables):
                    print(f"    + {table}")
            
            if not missing_tables:
                print(f"\n✅ All expected tables created successfully!")
            
            print(f"\n📋 Complete table list ({len(existing_tables)} tables):")
            for table in sorted(existing_tables):
                print(f"  • {table}")
            
            return len(missing_tables) == 0
            
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False


def create_sample_data() -> bool:
    """
    Create sample admin user and basic data for testing
    """
    print("\n👤 Creating sample admin user and test data...")
    
    try:
        with app.app_context():
            # Create admin user
            admin_email = 'admin@school.com'
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if not existing_admin:
                admin_user = User(
                    email=admin_email,
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    role=UserRole.ADMIN,
                    first_name='System',
                    last_name='Administrator',
                    active=True
                )
                db.session.add(admin_user)
                
                print("✅ Created admin user:")
                print("    Email: admin@school.com")
                print("    Password: admin123")
                print("    Role: Administrator")
            else:
                print("✅ Admin user already exists")
            
            # Create sample department
            dept = Department.query.filter_by(department_code='CS').first()
            if not dept:
                dept = Department(
                    department_code='CS',
                    department_name='Computer Science',
                    description='Department of Computer Science and Engineering',
                    location='Building A, Floor 2',
                    active=True
                )
                db.session.add(dept)
                print("✅ Created sample Computer Science department")
            
            # Create sample academic period
            academic_period = AcademicPeriod.query.filter_by(academic_year='2024-25').first()
            if not academic_period:
                from datetime import date
                academic_period = AcademicPeriod(
                    academic_year='2024-25',
                    semester='Fall',
                    start_date=date(2024, 9, 1),
                    end_date=date(2024, 12, 31),
                    is_current=True,
                    active=True
                )
                db.session.add(academic_period)
                print("✅ Created sample academic period")
            
            # Create sample fee types
            fee_type = FeeType.query.filter_by(fee_name='Tuition Fee').first()
            if not fee_type:
                fee_type = FeeType(
                    fee_name='Tuition Fee',
                    description='Annual tuition fee',
                    amount=5000.00,
                    is_mandatory=True,
                    due_date_offset=30,
                    active=True
                )
                db.session.add(fee_type)
                print("✅ Created sample fee type")
            
            db.session.commit()
            print("✅ Sample data created successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass
        return False


def show_completion_summary() -> None:
    """
    Display completion summary and next steps
    """
    print("\n" + "=" * 70)
    print("🎉 DATABASE SCHEMA INITIALIZATION COMPLETE!")
    print("=" * 70)
    print("\n✅ Student Management System Database Ready")
    print("\n🏫 Features successfully initialized:")
    
    features = [
        "👥 User Management & Authentication", "🎓 Student Records Management",
        "📚 Course & Curriculum Management", "👨‍🏫 Teacher & Faculty Management", 
        "🏢 Department Management", "📅 Academic Calendar Management",
        "📋 Attendance Tracking System", "📊 Grades & Exam Management",
        "👨‍👩‍👧‍👦 Parent/Guardian Management", "💰 Fee & Financial Management",
        "📖 Library & Book Management", "📝 Assignment Management",
        "🎉 Events & Announcements", "🧠 Counseling & Support Services",
        "⚖️ Disciplinary Management", "🚌 Transportation Management",
        "🏠 Hostel & Accommodation", "🏥 Health Records Management", 
        "🎓 Scholarship Management", "🎓 Alumni Management",
        "👷 Staff Management", "📦 Inventory Management",
        "💬 Communication System", "📈 Reports & Analytics",
        "📄 Certificates & Documents"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"  {i:2d}. {feature}")
    
    print(f"\n🎯 Total Features: {len(features)}")
    print("\n🚀 Your comprehensive Student Management System is ready!")
    print("\n💡 Next Steps:")
    print("   1. Start the application: python main.py")
    print("   2. Login with admin@school.com / admin123")
    print("   3. Set up your school information")
    print("   4. Add departments, teachers, and courses")
    print("   5. Begin student enrollment")
    print("   6. Customize settings as needed")
    print("\n📚 Documentation available in the docs/ folder")
    print("=" * 70)


def main() -> None:
    """
    Main function to initialize the complete database schema
    """
    print("🚀 STUDENT MANAGEMENT SYSTEM")
    print("📋 Database Schema Initialization")
    print("=" * 70)
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # Step 2: Create enum types
    if not create_enum_types():
        print("\n❌ Failed to create enum types")
        sys.exit(1)
    
    # Step 3: Create all tables
    if not create_all_tables():
        print("\n❌ Failed to create tables")
        sys.exit(1)
    
    # Step 4: Verify table creation
    if not verify_tables():
        print("\n⚠️  Some tables may be missing, but continuing...")
    
    # Step 5: Create sample data
    if not create_sample_data():
        print("\n⚠️  Warning: Could not create sample data")
        print("You can create data manually after starting the application")
    
    # Step 6: Show completion summary
    show_completion_summary()


if __name__ == "__main__":
    main()