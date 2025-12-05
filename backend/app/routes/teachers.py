"""
Teacher CRUD routes.
Handles all teacher-related operations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import mongo
from app.utils.decorators import handle_exceptions
from werkzeug.security import generate_password_hash
from datetime import datetime

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_all_teachers():
    """
    Retrieve all teachers.
    """
    teachers = list(mongo.db.teachers.find({}, {'_id': 0}))
    return jsonify({'teachers': teachers, 'count': len(teachers)}), 200

@teachers_bp.route('/', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_teacher():
    """
    Create a new teacher and associated user account.
    """
    data = request.get_json()
    
    required_fields = ['teacher_id', 'name', 'email', 'subject']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Check if teacher exists
    if mongo.db.teachers.find_one({'teacher_id': data['teacher_id']}):
        return jsonify({'error': 'Teacher ID already exists'}), 409
        
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already in use'}), 409

    # Create Teacher Document
    teacher_doc = {
        'teacher_id': data['teacher_id'],
        'name': data['name'],
        'email': data['email'],
        'subject': data['subject'],
        'phone': data.get('phone', ''),
        'qualification': data.get('qualification', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    mongo.db.teachers.insert_one(teacher_doc)

    # Create User Document
    # Default password is 'teacher123'
    hashed_password = generate_password_hash('teacher123')
    
    user_doc = {
        'username': data['teacher_id'], # Use teacher_id as username
        'email': data['email'],
        'password': hashed_password,
        'role': 'teacher',
        'full_name': data['name'],
        'teacher_id': data['teacher_id'],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True
    }
    
    mongo.db.users.insert_one(user_doc)

    teacher_doc.pop('_id', None)
    return jsonify({'message': 'Teacher created successfully', 'teacher': teacher_doc}), 201

@teachers_bp.route('/<teacher_id>', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_teacher(teacher_id):
    """
    Update a teacher's information.
    """
    data = request.get_json()
    
    teacher = mongo.db.teachers.find_one({'teacher_id': teacher_id})
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    update_data = {k: v for k, v in data.items() if k in ['name', 'email', 'subject', 'phone', 'qualification']}
    update_data['updated_at'] = datetime.utcnow()
    
    mongo.db.teachers.update_one({'teacher_id': teacher_id}, {'$set': update_data})
    
    # Sync with User collection if name or email changed
    user_update = {}
    if 'name' in update_data:
        user_update['full_name'] = update_data['name']
    if 'email' in update_data:
        user_update['email'] = update_data['email']
        
    if user_update:
        mongo.db.users.update_one({'teacher_id': teacher_id}, {'$set': user_update})

    return jsonify({'message': 'Teacher updated successfully'}), 200

@teachers_bp.route('/<teacher_id>', methods=['DELETE'])
@jwt_required()
@handle_exceptions
def delete_teacher(teacher_id):
    """
    Delete a teacher and associated user account.
    """
    teacher = mongo.db.teachers.find_one({'teacher_id': teacher_id})
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404

    mongo.db.teachers.delete_one({'teacher_id': teacher_id})
    mongo.db.users.delete_one({'teacher_id': teacher_id})

    return jsonify({'message': 'Teacher deleted successfully'}), 200
