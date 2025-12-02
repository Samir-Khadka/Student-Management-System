"""
Flask application factory module.
Creates and configures the Flask application instance.
"""
from flask import Flask, request, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
import logging
from datetime import datetime
from config.config import get_config
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

mongo_client = None
mongo_db = None

jwt = JWTManager()


class MongoWrapper:
    """Wrapper class to mimic Flask-PyMongo interface"""
    def __init__(self):
        self.db = None
        self.cx = None
    
    def init_app(self, app):
        """Initialize MongoDB connection"""
        try:
            uri = app.config.get('MONGO_URI')
            db_name = app.config.get('MONGODB_DB', 'student_management')
            
            try:
                import dns.resolver
                app.logger.info("DNS resolver available for MongoDB SRV")
            except ImportError:
                app.logger.warning("dnspython not available - SRV records may not work")
            
            self.cx = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                connect=False,
                directConnection=False
            )
            self.db = self.cx[db_name]
            app.logger.info(f"MongoDB client initialized for database: {db_name} (lazy connection)")
            
        except Exception as e:
            app.logger.warning(f"MongoDB initialization warning (will retry on first request): {str(e)}")
            self.db = None
            self.cx = None


mongo = MongoWrapper()


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Request logging
    @app.before_request
    def log_request_info():
        """Log incoming requests for debugging."""
        app.logger.debug(f"Incoming request: {request.method} {request.path}")
        if request.data:
            app.logger.debug(f"Request data: {request.data}")

    @app.after_request
    def log_response_info(response):
        """Log outgoing responses for debugging."""
        app.logger.debug(f"Response status: {response.status_code}")
        return response
    
    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint with API information."""
        return {
            'message': 'Student Management Backend API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'documentation': '/api/docs',
                'health_check': '/api/health',
                'authentication': '/api/auth',
                'students': '/api/students',
                'analytics': '/api/analytics'
            },
            'instructions': 'Visit /api/docs for API documentation'
        }
    
    # Favicon endpoint
    @app.route('/favicon.ico')
    def favicon():
        """Return a simple favicon or 204 No Content."""
        return Response(status=204)  # No Content
    
    config = get_config(config_name)
    app.config.from_object(config)
    
    mongo.init_app(app)
    
    CORS(app, 
         origins=config.CORS_ORIGINS,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    jwt.init_app(app)
    
    from app.swagger_config import SWAGGER_CONFIG, SWAGGER_TEMPLATE
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)
    
    setup_logging(app)
    
    register_blueprints(app)
    
    register_error_handlers(app)
    
    register_jwt_handlers(app)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'message': 'Student Management Backend is running',
            'timestamp': datetime.now().isoformat()
        }, 200
    
    return app


def register_blueprints(app: Flask) -> None:
    """
    Register all blueprints for the application.
    
    Args:
        app: Flask application instance
    """
    from app.routes.students import students_bp
    from app.routes.auth import auth_bp
    from app.routes.analytics import analytics_bp
    from app.routes.student_profile import student_profile_bp
    
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(student_profile_bp, url_prefix='/api/student')
    
    app.logger.info("Blueprints registered successfully")


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors with JSON response."""
        if request.path.startswith('/api/'):
            return {
                'error': 'Not Found',
                'message': f'The requested endpoint {request.path} was not found',
                'available_endpoints': [
                    '/api/health',
                    '/api/docs',
                    '/api/auth/login',
                    '/api/auth/register',
                    '/api/students',
                    '/api/analytics'
                ]
            }, 404
        else:
            # For non-API routes, return HTML with helpful info
            return f"""
            <html>
                <head><title>Page Not Found</title></head>
                <body>
                    <h1>404 - Page Not Found</h1>
                    <p>The requested page was not found.</p>
                    <p>Available endpoints:</p>
                    <ul>
                        <li><a href="/api/docs">API Documentation</a></li>
                        <li><a href="/api/health">Health Check</a></li>
                    </ul>
                </body>
            </html>
            """, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors with JSON response."""
        if request.path.startswith('/api/'):
            return {
                'error': 'Method Not Allowed',
                'message': f'The method {request.method} is not allowed for {request.path}',
                'allowed_methods': getattr(error, 'valid_methods', ['GET', 'POST', 'PUT', 'DELETE'])
            }, 405
        else:
            return f"""
            <html>
                <head><title>Method Not Allowed</title></head>
                <body>
                    <h1>405 - Method Not Allowed</h1>
                    <p>The method {request.method} is not allowed for this endpoint.</p>
                    <p>Please check the API documentation at <a href="/api/docs">/api/docs</a></p>
                </body>
            </html>
            """, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors with JSON response."""
        app.logger.error(f'Internal server error: {str(error)}')
        
        if request.path.startswith('/api/'):
            return {
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'timestamp': datetime.now().isoformat()
            }, 500
        else:
            return f"""
            <html>
                <head><title>Internal Server Error</title></head>
                <body>
                    <h1>500 - Internal Server Error</h1>
                    <p>An unexpected error occurred.</p>
                    <p>Please check the server logs for more details.</p>
                </body>
            </html>
            """, 500


def register_jwt_handlers(app: Flask) -> None:
    """
    Register JWT error handlers.
    
    Args:
        app: Flask application instance
    """
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token."""
        return {
            'error': 'Token Expired',
            'message': 'The token has expired. Please login again.',
            'code': 'token_expired'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token."""
        return {
            'error': 'Invalid Token',
            'message': 'The token is invalid. Please login again.',
            'code': 'token_invalid'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token."""
        return {
            'error': 'Authorization Required',
            'message': 'Request does not contain a valid access token',
            'code': 'authorization_required'
        }, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Handle revoked token."""
        return {
            'error': 'Token Revoked',
            'message': 'The token has been revoked. Please login again.',
            'code': 'token_revoked'
        }, 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """Handle non-fresh token."""
        return {
            'error': 'Fresh Token Required',
            'message': 'A fresh token is required for this endpoint',
            'code': 'fresh_token_required'
        }, 401


def setup_logging(app: Flask) -> None:
    """
    Setup logging configuration.
    
    Args:
        app: Flask application instance
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    
    # Create logs directory if it doesn't exist
    import os
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(app.config['LOG_FORMAT'])
    
    # File handler
    file_handler = logging.FileHandler(
        os.path.join(logs_dir, 'app.log')
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)