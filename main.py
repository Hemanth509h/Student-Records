# Import the Flask application instance from the core.app module
from core.app import app

# Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':
    # Run the Flask development server
    # host='0.0.0.0' - Makes the server publicly accessible (not just localhost)
    # port=5000 - The port number where the server will listen for requests
    # debug=True - Enables debug mode with auto-reload and detailed error messages
    app.run(host='0.0.0.0', port=5000, debug=True)
