#!/usr/bin/env python3
"""
Simple Database Initialization Script
=====================================

This script creates the basic database tables for the Student Management System.
It includes only the essential tables: users and students.

Usage:
    python create_tables.py
"""

import os
import sys
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.models import db, User, Student, UserRole
    from core.app import app
    print("✅ Successfully imported models and app")
except ImportError as e:
    print(f"❌ Error importing: {e}")
    sys.exit(1)

def create_tables():
    """Create all database tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    with app.app_context():
        try:
            admin = User.query.filter_by(email='admin@school.com').first()
            if not admin:
                admin = User(
                    email='admin@school.com',
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    role=UserRole.ADMIN,
                    first_name='System',
                    last_name='Administrator',
                    active=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created (email: admin@school.com, password: admin123)")
            else:
                print("ℹ️  Admin user already exists")
            return True
        except IntegrityError:
            db.session.rollback()
            print("ℹ️  Admin user already exists")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {e}")
            return False

def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("Student Management System - Database Setup")
    print("="*50 + "\n")
    
    if not create_tables():
        print("\n❌ Database initialization failed")
        sys.exit(1)
    
    if not create_admin_user():
        print("\n⚠️  Warning: Could not create admin user")
    
    print("\n" + "="*50)
    print("✅ Database initialization complete!")
    print("="*50)
    print("\nYou can now start the application.")
    print("Default login: admin@school.com / admin123\n")

if __name__ == "__main__":
    main()
