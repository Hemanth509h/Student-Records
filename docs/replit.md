# Student Record Management System

## Overview

This is a Flask-based web application for managing student records that demonstrates the practical implementation of custom data structures in software development. The system provides a comprehensive platform for storing, retrieving, querying, and analyzing student data using custom-built linked lists, stacks, and queues instead of traditional database systems. It serves as both a functional student management tool and an educational demonstration of how fundamental computer science concepts can be applied to solve real-world problems.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Web Framework**: Flask serves as the main application layer providing RESTful routes, template rendering, and request handling
- **Custom Data Structures**: Primary storage uses linked lists for student records, stacks for operation history/undo functionality, and queues for batch processing
- **Business Logic Layer**: Modular design with StudentManager handling CRUD operations and QueryEngine providing SQL-like query processing capabilities
- **File Persistence**: JSON-based storage system with automatic save/load functionality for data persistence across sessions

### Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template providing consistent dark theme layout
- **Styling Framework**: Bootstrap 5 with custom CSS implementing a modern dark theme design
- **Client-Side Scripting**: Vanilla JavaScript for form validation, interactive features, search functionality, and real-time user feedback
- **Responsive Design**: Mobile-first approach ensuring functionality across different screen sizes and devices

### Data Management Design
- **LinkedList Implementation**: Custom node-based structure supporting append, prepend, delete, find, search, and update operations with O(n) complexity
- **Stack Implementation**: LIFO structure for operation history tracking with configurable capacity limits for undo functionality
- **Query Processing Engine**: SQL-like interface supporting SELECT, WHERE, ORDER BY, LIMIT, and GROUP BY operations on custom data structures
- **StudentDataProcessor**: Specialized utility class for logging operations, data validation, and batch processing capabilities

### Security and Session Management
- **Session Handling**: Flask sessions with environment-configurable secret keys for production security
- **Input Validation**: Comprehensive form validation on both client and server sides with sanitization
- **Error Handling**: Robust error handling with user-friendly flash messages and graceful failure recovery

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: Comprehensive UI framework providing responsive grid system, components, and utilities delivered via CDN
- **Font Awesome 6.4.0**: Icon library providing consistent visual elements and improved user interface experience
- **CDN Delivery**: External content delivery networks used for faster loading times and reduced server bandwidth

### Python Dependencies
- **Flask**: Core web framework handling routing, templating, request processing, and application lifecycle management
- **Standard Library Modules**: Leverages built-in Python modules including json for data serialization, os for environment variables, and psycopg2 for potential database integration
- **Custom Module Architecture**: Self-contained modules for data structures, student management, and query processing without external library dependencies

### Development Environment
- **Replit Platform**: Configured for cloud-based development with proper host binding and port configuration
- **Environment Variables**: Uses DATABASE_URL and SESSION_SECRET for configuration management
- **Debug Mode**: Development-optimized settings with hot reload and detailed error reporting capabilities