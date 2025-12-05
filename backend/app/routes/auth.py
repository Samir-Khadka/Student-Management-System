"""
Authentication routes.
Handles user registration, login, logout, and JWT management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token
)
from app import mongo
from app.utils.auth_helper import (
    hash_password,
    verify_password,
    generate_tokens,
    validate_user_data
)
from app.utils.decorators import handle_exceptions
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@handle_exceptions
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
            - email
            - role
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "password123"
            email:
              type: string
              example: "john@example.com"
            role:
              type: string
              enum: [student, teacher, admin]
              example: "student"
            student_id:
              type: string
              description: Required if role is student
              example: "S001"
            full_name:
              type: string
              example: "John Doe"
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Username already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    validated_data, error = validate_user_data(data)
    if error:
        return jsonify({'error': 'Validation Error', 'message': error}), 400
    
    existing_user = mongo.db.users.find_one({'username': validated_data['username']})
    if existing_user:
        return jsonify({
            'error': 'Conflict',
            'message': 'Username already exists'
        }), 409
    
    existing_email = mongo.db.users.find_one({'email': validated_data['email']})
    if existing_email:
        return jsonify({
            'error': 'Conflict',
            'message': 'Email already exists'
        }), 409
    
    # If role is student, ensure student_id is provided
    if validated_data['role'] == 'student' and 'student_id' not in data:
        return jsonify({
            'error': 'Validation Error',
            'message': 'student_id is required for student role'
        }), 400
    
    hashed_pwd = hash_password(validated_data['password'])
    
    user_doc = {
        'username': validated_data['username'],
        'password': hashed_pwd,
        'email': validated_data['email'],
        'role': validated_data['role'],
        'full_name': data.get('full_name', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True
    }
    
    if 'student_id' in data:
        user_doc['student_id'] = data['student_id']
        
        # Check if student_id already exists in students collection
        if mongo.db.students.find_one({'student_id': data['student_id']}):
            return jsonify({
                'error': 'Conflict',
                'message': f"Student ID {data['student_id']} already exists"
            }), 409
    
    result = mongo.db.users.insert_one(user_doc)
    
    # If role is student, create entry in students collection
    if validated_data['role'] == 'student':
        student_doc = {
            'student_id': data['student_id'],
            'name': data.get('full_name', validated_data['username']),
            'age': 0,  # Default
            'gender': 'Other',  # Default
            'study_time': 0,
            'absences': 0,
            'parental_support': 'medium',
            'internet_access': False,
            'final_grade': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.students.insert_one(student_doc)

    # If role is teacher, create entry in teachers collection
    elif validated_data['role'] == 'teacher':
        # Use username as teacher_id if not provided (though registration form usually doesn't ask for teacher_id)
        # For consistency, we'll use the username as teacher_id
        teacher_doc = {
            'teacher_id': validated_data['username'],
            'name': data.get('full_name', validated_data['username']),
            'email': validated_data['email'],
            'subject': 'General',  # Default
            'phone': '',
            'qualification': '',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.teachers.insert_one(teacher_doc)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(result.inserted_id),
        'username': validated_data['username'],
        'role': validated_data['role']
    }), 201


@auth_bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    """
    Login and get JWT tokens.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            user:
              type: object
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Username and password are required'
        }), 400
    
    # Find user
    user = mongo.db.users.find_one({'username': data['username']})
    
    if not user:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid username or password'
        }), 401
    
    if not user.get('is_active', True):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Account is deactivated'
        }), 401
    
    if not verify_password(data['password'], user['password']):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid username or password'
        }), 401
    
    tokens = generate_tokens(str(user['_id']), user['role'])
    
    # Log successful login
    from flask import current_app
    current_app.logger.info(f"User {user['username']} logged in successfully")
    
    return jsonify({
        'message': 'Login successful',
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': {
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'full_name': user.get('full_name', ''),
            'student_id': user.get('student_id', None)
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_exceptions
def refresh():
    """
    Refresh access token using refresh token.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token
      401:
        description: Invalid refresh token
    """
    current_user_id = get_jwt_identity()
    
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'User not found'
        }), 401
    
    access_token = create_access_token(
        identity=current_user_id,
        additional_claims={'role': user['role']}
    )
    
    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@handle_exceptions
def logout():
    """
    Logout user.
    In JWT stateless authentication, actual logout is handled by client.
    This endpoint logs the logout event and provides confirmation.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
      401:
        description: Invalid token
    """
    try:
        # Get JWT identity
        current_user_id = get_jwt_identity()
        
        # Get user information for logging
        from bson.objectid import ObjectId
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        
        if user:
            # Log the logout event
            from flask import current_app
            current_app.logger.info(f"User {user['username']} (ID: {current_user_id}) logged out successfully")
            
            # Optionally update last logout time in user document
            mongo.db.users.update_one(
                {'_id': ObjectId(current_user_id)},
                {'$set': {'last_logout': datetime.utcnow()}}
            )
        
        return jsonify({
            'message': 'Logout successful',
            'logout_time': datetime.utcnow().isoformat(),
            'instruction': 'Please delete the JWT token on client side to complete logout'
        }), 200
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Logout error: {str(e)}")
        
        return jsonify({
            'error': 'Logout failed',
            'message': 'An error occurred during logout'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_current_user():
    """
    Get current user information.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user information
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({
            'error': 'Not Found',
            'message': 'User not found'
        }), 404
    
    return jsonify({
        'user': {
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'full_name': user.get('full_name', ''),
            'student_id': user.get('student_id', None),
            'created_at': user.get('created_at', None),
            'is_active': user.get('is_active', True),
            'last_logout': user.get('last_logout', None)
        }
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@handle_exceptions
def change_password():
    """
    Change user password.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              example: "oldpassword123"
            new_password:
              type: string
              example: "newpassword123"
    responses:
      200:
        description: Password changed successfully
      400:
        description: Invalid current password
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Current password and new password are required'
        }), 400
    
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({
            'error': 'Not Found',
            'message': 'User not found'
        }), 404
    
    # Verify current password
    if not verify_password(data['current_password'], user['password']):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Current password is incorrect'
        }), 401
    
    # Validate new password
    if len(data['new_password']) < 6:
        return jsonify({
            'error': 'Validation Error',
            'message': 'New password must be at least 6 characters long'
        }), 400
    
    # Hash new password
    new_hashed_password = hash_password(data['new_password'])
    
    # Update password
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {
            '$set': {
                'password': new_hashed_password,
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    # Log password change
    from flask import current_app
    current_app.logger.info(f"User {user['username']} changed password successfully")
    
    return jsonify({
        'message': 'Password changed successfully',
        'changed_at': datetime.utcnow().isoformat()
    }), 200
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    update_data = {}
    if 'full_name' in data:
        update_data['full_name'] = data['full_name']
    if 'email' in data:
        existing = mongo.db.users.find_one({'email': data['email']})
        if existing and str(existing['_id']) != current_user_id:
            return jsonify({'error': 'Email already in use'}), 409
        update_data['email'] = data['email']
        
    if not update_data:
        return jsonify({'message': 'No changes made'}), 200
        
    update_data['updated_at'] = datetime.utcnow()
    
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {'$set': update_data}
    )
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': {
            'full_name': update_data.get('full_name', user.get('full_name')),
            'email': update_data.get('email', user.get('email'))
        }
    }), 200


@auth_bp.route('/upload-picture', methods=['POST'])
@jwt_required()
@handle_exceptions
def upload_picture():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        filename = secure_filename(file.filename)
        unique_filename = f'{get_jwt_identity()}_{int(datetime.utcnow().timestamp())}_{filename}'
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        relative_path = f'/static/uploads/{unique_filename}'
        
        from bson.objectid import ObjectId
        mongo.db.users.update_one(
            {'_id': ObjectId(get_jwt_identity())},
            {'$set': {'profile_picture': relative_path}}
        )
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'profile_picture': relative_path
        }), 200

