"""
Custom decorators for the application.
"""
from functools import wraps
from flask import request, jsonify
import logging
import traceback

logger = logging.getLogger(__name__)


def require_json(f):
    """Decorator to require JSON content type."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'error': 'Invalid Request',
                'message': 'Request content type must be application/json'
            }), 400
        return f(*args, **kwargs)
    return decorated_function


def handle_exceptions(f):
    """Decorator to handle exceptions in routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({
                'error': 'Validation Error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': 'Server Error',
                'message': str(e)
            }), 500
    return decorated_function
