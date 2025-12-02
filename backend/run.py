"""
Application entry point.
Run this file to start the Flask development server.

Usage:
    python run.py
"""
import os
from app import create_app

if __name__ == '__main__':
    # Get environment from env variable or default to development
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask app
    app = create_app(env)
    
    # Get host and port from environment
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 5000))
    debug = app.config['DEBUG']
    
    # Run the app
    app.run(host=host, port=port, debug=debug)
