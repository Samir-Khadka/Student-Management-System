"""
Student profile routes.
Students can view and update their own profiles.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app import mongo
from app.utils.decorators import handle_exceptions
from app.models.student_model import validate_student_data, serialize_student

from bson.objectid import ObjectId

student_profile_bp = Blueprint('student_profile', __name__)


@student_profile_bp.route('/profile', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_my_profile():
    """
    Get current student's profile.
    ---
    tags:
      - Student Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Student profile
      403:
        description: Forbidden - Only students can access
      404:
        description: Student not found
    """
    claims = get_jwt()
    role = claims.get('role')
    user_id = get_jwt_identity()
    
    if role != 'student':
        return jsonify({
            'error': 'Forbidden',
            'message': 'Only students can access this endpoint'
        }), 403
    
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user or 'student_id' not in user:
        return jsonify({
            'error': 'Not Found',
            'message': 'Student profile not found'
        }), 404
    
    student = mongo.db.students.find_one({'student_id': user['student_id']})
    if not student:
        return jsonify({
            'error': 'Not Found',
            'message': 'Student record not found'
        }), 404
    
    return jsonify(serialize_student(student)), 200


@student_profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_my_profile():
    """
    Update current student's profile.
    Students can only update limited fields.
    ---
    tags:
      - Student Profile
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            study_time:
              type: integer
            internet_access:
              type: boolean
            attendance_log:
              type: array
              items:
                type: object
    responses:
      200:
        description: Profile updated
      403:
        description: Forbidden - Only students can access
      404:
        description: Student not found
    """
    claims = get_jwt()
    role = claims.get('role')
    user_id = get_jwt_identity()
    
    if role != 'student':
        return jsonify({
            'error': 'Forbidden',
            'message': 'Only students can access this endpoint'
        }), 403
    
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user or 'student_id' not in user:
        return jsonify({
            'error': 'Not Found',
            'message': 'Student profile not found'
        }), 404
    
    data = request.get_json()
    
    allowed_fields = {'study_time', 'internet_access', 'attendance_log'}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'No valid fields to update. Allowed: study_time, internet_access, attendance_log'
        }), 400
    
    try:
        validate_student_data(update_data, partial=True)
    except Exception as e:
        return jsonify({
            'error': 'Validation Error',
            'message': str(e)
        }), 400
    
    result = mongo.db.students.update_one(
        {'student_id': user['student_id']},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        return jsonify({
            'error': 'Not Found',
            'message': 'Student record not found'
        }), 404
    
    updated_student = mongo.db.students.find_one({'student_id': user['student_id']})
    
    return jsonify({
        'message': 'Profile updated successfully',
        'student': serialize_student(updated_student)
    }), 200


@student_profile_bp.route('/profile/prediction', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_my_prediction():
    """
    Get prediction for current student.
    ---
    tags:
      - Student Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Prediction result
      403:
        description: Forbidden - Only students can access
      404:
        description: Student not found
    """
    claims = get_jwt()
    role = claims.get('role')
    user_id = get_jwt_identity()
    
    if role != 'student':
        return jsonify({
            'error': 'Forbidden',
            'message': 'Only students can access this endpoint'
        }), 403
    
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user or 'student_id' not in user:
        return jsonify({
            'error': 'Not Found',
            'message': 'Student profile not found'
        }), 404
    
    student = mongo.db.students.find_one({'student_id': user['student_id']})
    if not student:
        return jsonify({
            'error': 'Not Found',
            'message': 'Student record not found'
        }), 404
    
    from app.models.student_model import predict_student_performance
    
    prediction = predict_student_performance(student)
    
    return jsonify({
        'student_id': student['student_id'],
        'name': student['name'],
        'prediction': prediction
    }), 200
