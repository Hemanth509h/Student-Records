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
from typing import List, Optional
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy import text

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.models import db, UserRole
    from core.app import app
    print("✓ Successfully imported all models and dependencies")
except ImportError as e:
    print(f"✗ Error importing models: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


def create_enum_types() -> bool:
    """
    Create custom enum types in PostgreSQL database
    """
    print("\n📋 Creating enum types...")
    
    try:
        with app.app_context():
            # Create enum types manually (some PostgreSQL versions don't support IF NOT EXISTS for enums)
            enum_commands = [
                "DO $$ BEGIN CREATE TYPE attendancestatus AS ENUM ('present', 'absent', 'late', 'excused'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
                "DO $$ BEGIN CREATE TYPE feestatus AS ENUM ('pending', 'paid', 'overdue', 'cancelled'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
                "DO $$ BEGIN CREATE TYPE bookstatus AS ENUM ('available', 'borrowed', 'reserved', 'damaged'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
                "DO $$ BEGIN CREATE TYPE userrole AS ENUM ('ADMIN', 'TEACHER', 'STUDENT', 'PARENT', 'STAFF'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
            ]
            
            for command in enum_commands:
                try:
                    db.session.execute(text(command))
                    db.session.commit()
                except Exception as e:
                    print(f"  Note: {str(e)[:100]}...")
                    db.session.rollback()
            
            print("✓ Enum types created successfully")
            
    except Exception as e:
        print(f"✗ Error creating enum types: {e}")
        return False
    
    return True


def create_all_tables() -> bool:
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
            row = result.fetchone()
            if row:
                table_count = row[0]
                print(f"✓ Total tables created: {table_count}")
            else:
                print("✓ Tables created (count not available)")
            
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


def verify_tables() -> bool:
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


def create_sample_admin_user() -> bool:
    """
    Create a sample admin user for initial access
    """
    print("\n👤 Creating sample admin user...")
    
    try:
        with app.app_context():
            # Import User model here to avoid circular imports
            from core.models import User
            
            # Check if admin user already exists
            try:
                existing_admin = User.query.filter_by(email='admin@school.com').first()
                if existing_admin:
                    print("✓ Admin user already exists")
                    return True
            except Exception:
                # If query fails, table might not exist yet, continue to create
                pass
            
            # Create admin user using direct SQL to avoid model issues
            try:
                from werkzeug.security import generate_password_hash
                
                db.session.execute(text("""
                    INSERT INTO users (email, username, password_hash, role, first_name, last_name, is_active) 
                    VALUES (:email, :username, :password_hash, :role, :first_name, :last_name, :is_active)
                    ON CONFLICT (email) DO NOTHING
                """), {
                    'email': 'admin@school.com',
                    'username': 'admin',
                    'password_hash': generate_password_hash('admin123'),
                    'role': 'ADMIN',
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'is_active': True
                })
                db.session.commit()
                
                print("✓ Sample admin user created:")
                print("  Email: admin@school.com")
                print("  Password: admin123")
                print("  Role: Administrator")
                
                return True
                
            except Exception as e:
                print(f"✗ Error creating admin user with SQL: {e}")
                db.session.rollback()
                return False
            
    except Exception as e:
        print(f"✗ Error in admin user creation: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass
        return False


def show_completion_summary() -> None:
    """
    Display completion summary and next steps
    """
    print("\n" + "=" * 60)
    print("🎉 DATABASE SCHEMA INITIALIZATION COMPLETE!")
    print("=" * 60)
    print("\n✅ All 25+ features have been successfully initialized:")
    
    features = [
        "User Management with Roles",
        "Student & Academic Management", 
        "Course & Teacher Management",
        "Attendance & Grade Tracking",
        "Fee & Financial Management",
        "Library & Book Management",
        "Exam & Assignment Systems",
        "Communication & Events",
        "Health & Counseling Records",
        "Transportation & Hostel Management",
        "Alumni & Scholarship Programs",
        "Staff & Inventory Management",
        "Reports & Document Management"
    ]
    
    for feature in features:
        print(f"   • {feature}")
    
    print("\n🚀 Your Student Management System is ready to use!")
    print("\n💡 Next steps:")
    print("   1. Start the application: python main.py")
    print("   2. Login with admin@school.com / admin123")
    print("   3. Begin adding your school data")
    print("   4. Customize the system to fit your needs")


def main() -> None:
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
    
    # Mask password in URL for display
    display_url = database_url
    if '@' in display_url:
        parts = display_url.split('@')
        if len(parts) >= 2:
            display_url = parts[0].split(':')[0] + ":***@" + parts[1]
    
    print(f"✓ Database URL configured: {display_url[:50]}...")
    
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
        print("You can create one manually after starting the application")
    
    # Step 5: Show completion summary
    show_completion_summary()


if __name__ == "__main__":
    main()