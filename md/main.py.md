# main.py - Application Entry Point

## Overview
This is the main entry point for the Student Record Management System web application. It serves as the bootstrap file that starts the Flask development server.

## Purpose
- **Primary Function**: Start the Flask web server
- **Environment**: Development server configuration
- **Import**: Imports the Flask app instance from the core module

## Code Structure

### Imports
```python
from core.app import app
```
- Imports the main Flask application instance from the core module

### Main Execution
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## Configuration Details
- **Host**: `0.0.0.0` - Allows external connections (required for Replit environment)
- **Port**: `5000` - Standard development port for Flask applications
- **Debug Mode**: `True` - Enables auto-reload and detailed error messages during development

## Key Features
- **Hot Reload**: Automatically restarts server when code changes are detected
- **Error Handling**: Displays detailed error messages in debug mode
- **External Access**: Configured to accept connections from external interfaces

## Usage
Run this file directly to start the web server:
```bash
python main.py
```

## Security Note
The debug mode should be disabled in production environments for security reasons.