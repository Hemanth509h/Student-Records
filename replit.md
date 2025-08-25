# Student Record Management System

## Overview

This is a Flask-based web application for managing student records with a custom data structures implementation. The system provides a comprehensive platform for storing, retrieving, querying, and analyzing student data including grades, courses, and personal information. It features a SQL-like query interface, custom linked list and stack data structures for efficient data manipulation, and a responsive dark-themed web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework serving as the main application layer
- **Data Layer**: Custom implementation using linked lists and stacks instead of traditional databases
- **Business Logic**: Modular design with separate managers for student operations and query processing
- **File Storage**: JSON-based persistence for student data with automatic save/load functionality

### Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template providing consistent layout
- **Styling**: Bootstrap 5 with custom CSS for dark theme implementation
- **JavaScript**: Vanilla JavaScript for form validation, interactive features, and user experience enhancements
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Data Structures Design
- **LinkedList**: Custom implementation for storing student records with append, prepend, delete, and search operations
- **Stack**: Operation history tracking for undo functionality with configurable size limits
- **StudentDataProcessor**: Specialized processor for logging and managing student data operations

### Query Engine Architecture
- **SQL-like Interface**: Custom query parser supporting SELECT, WHERE, ORDER BY, LIMIT, and GROUP BY operations
- **Query Processing**: Multi-stage pipeline for parsing, filtering, sorting, and result formatting
- **Flexible Filtering**: Support for various comparison operators and field-based searches

### Authentication & Session Management
- **Session Handling**: Flask sessions with configurable secret keys
- **Security**: Environment-based configuration for production deployments
- **Error Handling**: Comprehensive error handling with user-friendly flash messages

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework for responsive design and components
- **Font Awesome 6.4.0**: Icon library for consistent visual elements
- **CDN Delivery**: External CDN links for faster loading and reduced server load

### Python Dependencies
- **Flask**: Core web framework for routing, templating, and request handling
- **Standard Library**: Uses built-in modules for JSON processing, logging, and file operations
- **No Database**: Deliberately avoids external database dependencies in favor of custom data structures

### Development Tools
- **Environment Variables**: Configuration through environment variables for security
- **Logging**: Built-in Python logging for debugging and monitoring
- **Debug Mode**: Flask debug mode for development with hot reloading

### File System Dependencies
- **JSON Storage**: Persistent data storage in student_data.json file
- **Static Assets**: CSS and JavaScript files served through Flask's static file handling
- **Template System**: HTML templates organized in the templates directory