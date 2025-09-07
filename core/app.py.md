# core/app.py - Main Flask Web Application

## Overview
The core Flask application that handles all web routes, request processing, and user interface for the Student Record Management System. This file contains the complete web framework implementation with 278 lines of code.

## Purpose
- **Web Framework**: Main Flask application with route handlers
- **User Interface**: Renders HTML templates and processes forms
- **Business Logic Integration**: Connects web layer to student management and query engine
- **Session Management**: Handles user sessions and flash messages

## Key Dependencies
```python
import os, logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from core.student_manager import StudentManager
from core.query_engine import QueryEngine
```

## Core Components

### Flask Application Setup
- **Secret Key**: Configured from environment variables for session security
- **Logging**: Debug-level logging enabled for development
- **Managers**: Initializes StudentManager and QueryEngine instances

### Route Handlers

#### 1. Dashboard Route (`/`)
- **Function**: `index()`
- **Purpose**: Main dashboard displaying all students and statistics
- **Features**: Shows total students, courses count, and average grades

#### 2. Student Management Routes
- **Add Student** (`/add_student`): Create new student records with validation
- **Edit Student** (`/edit_student/<roll_no>`): Modify existing student information
- **Delete Student** (`/delete_student/<roll_no>`): Remove students from system

#### 3. Advanced Features Routes
- **Query Interface** (`/query`): SQL-like query execution
- **Reports** (`/reports`): Analytics and performance statistics
- **Search** (`/search`): Multi-field student search functionality
- **Export** (`/export`): JSON data export for backup

## Form Processing & Validation
- **Input Sanitization**: Strips whitespace from all form inputs
- **Data Validation**: Ensures required fields are present
- **Type Validation**: Validates numeric grades and course-grade matching
- **Error Handling**: Comprehensive try-catch blocks with user feedback

## Features Implemented

### CRUD Operations
- **Create**: Add new students with courses and grades
- **Read**: Display students in organized dashboard
- **Update**: Edit existing student records
- **Delete**: Remove students with confirmation messages

### Advanced Analytics
- **Grade Distribution**: A, B, C, D, F categorization
- **Course Statistics**: Performance metrics per course
- **Top Performers**: Identification of high-achieving students
- **Attention Alerts**: Students with grades below 70%

### Data Management
- **Search Functionality**: Search across name, email, roll number
- **Export Feature**: Download data in JSON format
- **Query Engine**: Execute complex SQL-like queries
- **Real-time Statistics**: Live dashboard updates

## Error Handling Strategy
- **Flash Messages**: User-friendly error and success notifications
- **Exception Logging**: Detailed error logging for debugging
- **Graceful Degradation**: Continues operation even if individual features fail
- **Input Validation**: Prevents invalid data from entering the system

## Template Integration
- **Jinja2 Templates**: Dynamic HTML generation
- **Bootstrap Styling**: Responsive design with dark theme
- **Form Handling**: POST request processing with validation
- **Template Variables**: Data passing to frontend templates

## Security Features
- **Session Management**: Secure session handling with secret keys
- **Input Validation**: Sanitization of all user inputs
- **Error Messages**: Generic error messages to prevent information leakage
- **Environment Configuration**: Secret keys from environment variables

## Performance Considerations
- **Efficient Data Access**: Direct integration with custom data structures
- **Minimal Database Queries**: Uses in-memory operations where possible
- **Response Optimization**: Quick template rendering with preprocessed data
- **Error Recovery**: Fast error handling without system crashes