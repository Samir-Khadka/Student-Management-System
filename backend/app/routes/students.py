"""
Student CRUD routes.
Handles all student-related operations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import mongo
from app.models.student_model import (
    validate_student_data,
    serialize_student,
    predict_student_performance
)
from app.utils.decorators import handle_exceptions
from marshmallow import ValidationError
from bson.objectid import ObjectId
from datetime import datetime

students_bp = Blueprint('students', __name__)


@students_bp.route('/', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_student():
    """
    Create a new student.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - student_id
            - name
            - age
            - gender
            - study_time
            - absences
            - parental_support
            - internet_access
            - final_grade
          properties:
            student_id:
              type: string
              example: "S001"
            name:
              type: string
              example: "John Doe"
            age:
              type: integer
              example: 16
            gender:
              type: string
              enum: [Male, Female, Other]
            study_time:
              type: integer
              example: 10
            absences:
              type: integer
              example: 3
            parental_support:
              type: string
              enum: [low, medium, high]
            internet_access:
              type: boolean
            final_grade:
              type: integer
              minimum: 0
              maximum: 100
    responses:
      201:
        description: Student created successfully
      400:
        description: Validation error
      409:
        description: Student ID already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        validated_data = validate_student_data(data)
        
        existing = mongo.db.students.find_one({'student_id': validated_data['student_id']})
        if existing:
            return jsonify({
                'error': 'Conflict',
                'message': f"Student with ID {validated_data['student_id']} already exists"
            }), 409
        
        validated_data['created_at'] = datetime.utcnow()
        validated_data['updated_at'] = datetime.utcnow()
        
        result = mongo.db.students.insert_one(validated_data)
        
        student = mongo.db.students.find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'Student created successfully',
            'student': serialize_student(student)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': str(e.messages)
        }), 400


@students_bp.route('/', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_all_students():
    """
    Retrieve all students with optional filtering.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: query
        name: gender
        type: string
        description: Filter by gender
      - in: query
        name: min_grade
        type: integer
        description: Minimum final grade
      - in: query
        name: max_grade
        type: integer
        description: Maximum final grade
      - in: query
        name: limit
        type: integer
        description: Number of results to return
        default: 100
      - in: query
        name: skip
        type: integer
        description: Number of results to skip
        default: 0
    responses:
      200:
        description: List of students
    """
    query = {}
    
    if request.args.get('gender'):
        query['gender'] = request.args.get('gender')
    
    if request.args.get('min_grade'):
        query['final_grade'] = {'$gte': int(request.args.get('min_grade'))}
    
    if request.args.get('max_grade'):
        if 'final_grade' in query:
            query['final_grade']['$lte'] = int(request.args.get('max_grade'))
        else:
            query['final_grade'] = {'$lte': int(request.args.get('max_grade'))}
    
    limit = int(request.args.get('limit', 100))
    skip = int(request.args.get('skip', 0))
    
    students_cursor = mongo.db.students.find(query).skip(skip).limit(limit)
    students = [serialize_student(s) for s in students_cursor]
    
    total_count = mongo.db.students.count_documents(query)
    
    return jsonify({
        'students': students,
        'total': total_count,
        'count': len(students),
        'skip': skip,
        'limit': limit
    }), 200


@students_bp.route('/<student_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_student(student_id):
    """
    Retrieve a single student by student_id.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
        description: Student ID (e.g., S001)
    responses:
      200:
        description: Student details
      404:
        description: Student not found
    """
    student = mongo.db.students.find_one({'student_id': student_id})
    
    if not student:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    return jsonify({
        'student': serialize_student(student)
    }), 200


@students_bp.route('/<student_id>', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_student(student_id):
    """
    Update a student's information.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            age:
              type: integer
            gender:
              type: string
            study_time:
              type: integer
            absences:
              type: integer
            parental_support:
              type: string
            internet_access:
              type: boolean
            final_grade:
              type: integer
    responses:
      200:
        description: Student updated successfully
      404:
        description: Student not found
      400:
        description: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    existing = mongo.db.students.find_one({'student_id': student_id})
    if not existing:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    try:
        validated_data = validate_student_data(data, partial=True)
        
        if 'student_id' in validated_data:
            del validated_data['student_id']
        
        validated_data['updated_at'] = datetime.utcnow()
        
        mongo.db.students.update_one(
            {'student_id': student_id},
            {'$set': validated_data}
        )
        
        # Sync name change to users collection
        if 'name' in validated_data:
            mongo.db.users.update_one(
                {'student_id': student_id},
                {'$set': {'full_name': validated_data['name']}}
            )
        
        student = mongo.db.students.find_one({'student_id': student_id})
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': serialize_student(student)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': str(e.messages)
        }), 400


@students_bp.route('/<student_id>', methods=['DELETE'])
@jwt_required()
@handle_exceptions
def delete_student(student_id):
    """
    Delete a student.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
    responses:
      200:
        description: Student deleted successfully
      404:
        description: Student not found
    """
    existing = mongo.db.students.find_one({'student_id': student_id})
    if not existing:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    # Delete from students collection
    mongo.db.students.delete_one({'student_id': student_id})
    
    # Delete from users collection (associated account)
    mongo.db.users.delete_one({'student_id': student_id})
    
    return jsonify({
        'message': f'Student {student_id} and associated account deleted successfully'
    }), 200


@students_bp.route('/predict/<student_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def predict_performance(student_id):
    """
    Predict student pass/fail performance.
    ---
    tags:
      - Students
      - Predictions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
    responses:
      200:
        description: Prediction result
      404:
        description: Student not found
    """
    student = mongo.db.students.find_one({'student_id': student_id})
    
    if not student:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    prediction = predict_student_performance(student)
    
    return jsonify({
        'prediction': prediction
    }), 200
