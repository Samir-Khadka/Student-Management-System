"""
Authentication helper utilities.
Provides JWT token management and password hashing.
"""
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def hash_password(password):
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    """Verify a password against its hash."""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_tokens(user_id, role='student'):
    """Generate JWT access and refresh tokens."""
    additional_claims = {'role': role}
    
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def role_required(required_role):
    """Decorator to restrict access based on user role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', 'student')
            
            if user_role == 'admin':
                return fn(*args, **kwargs)
            
            if required_role == 'teacher' and user_role not in ['teacher', 'admin']:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Teacher access required'
                }), 403
            
            if required_role == 'admin' and user_role != 'admin':
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Admin access required'
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_user_data(data, is_update=False):
    """Validate user registration/update data."""
    if not is_update:
        required_fields = ['username', 'password', 'email', 'role']
        for field in required_fields:
            if field not in data:
                return None, f"Missing required field: {field}"
    
    if 'role' in data and data['role'] not in ['student', 'teacher', 'admin']:
        return None, "Invalid role. Must be: student, teacher, or admin"
    
    if 'email' in data and '@' not in data['email']:
        return None, "Invalid email format"
    
    if 'password' in data and len(data['password']) < 6:
        return None, "Password must be at least 6 characters"
    
    return data, None
