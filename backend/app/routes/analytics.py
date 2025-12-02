"""
Analytics routes.
Provides statistical analysis and insights on student data.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import mongo
from app.utils.auth_helper import role_required
from app.utils.decorators import handle_exceptions

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/average_grade', methods=['GET'])
@jwt_required()
@handle_exceptions
def average_grade():
    """
    Calculate average final grade across all students.
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    parameters:
      - in: query
        name: gender
        type: string
        description: Filter by gender
      - in: query
        name: parental_support
        type: string
        description: Filter by parental support level
    responses:
      200:
        description: Average grade statistics
    """
    # Build match filter
    match_filter = {}
    
    if request.args.get('gender'):
        match_filter['gender'] = request.args.get('gender')
    
    if request.args.get('parental_support'):
        match_filter['parental_support'] = request.args.get('parental_support')
    
    pipeline = []
    
    if match_filter:
        pipeline.append({'$match': match_filter})
    
    pipeline.extend([
        {
            '$group': {
                '_id': None,
                'average_grade': {'$avg': '$final_grade'},
                'min_grade': {'$min': '$final_grade'},
                'max_grade': {'$max': '$final_grade'},
                'total_students': {'$sum': 1}
            }
        }
    ])
    
    result = list(mongo.db.students.aggregate(pipeline))
    
    if not result:
        return jsonify({
            'average_grade': 0,
            'min_grade': 0,
            'max_grade': 0,
            'total_students': 0,
            'filters': match_filter
        }), 200
    
    stats = result[0]
    
    return jsonify({
        'average_grade': round(stats['average_grade'], 2),
        'min_grade': stats['min_grade'],
        'max_grade': stats['max_grade'],
        'total_students': stats['total_students'],
        'filters': match_filter
    }), 200


@analytics_bp.route('/at_risk_students', methods=['GET'])
@jwt_required()
@handle_exceptions
def at_risk_students():
    """
    Get list of students at risk of failing (grade < 40).
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    parameters:
      - in: query
        name: threshold
        type: integer
        default: 40
        description: Grade threshold for at-risk classification
    responses:
      200:
        description: List of at-risk students
    """
    threshold = int(request.args.get('threshold', 40))
    
    at_risk = list(mongo.db.students.find(
        {'final_grade': {'$lt': threshold}},
        {
            'student_id': 1,
            'name': 1,
            'final_grade': 1,
            'absences': 1,
            'study_time': 1,
            'parental_support': 1,
            '_id': 0
        }
    ).sort('final_grade', 1))
    
    for student in at_risk:
        risk_factors = []
        if student['final_grade'] < 30:
            risk_factors.append('Critical grade level')
        if student['absences'] > 10:
            risk_factors.append('High absences')
        if student['study_time'] < 5:
            risk_factors.append('Low study time')
        if student['parental_support'] == 'low':
            risk_factors.append('Low parental support')
        
        student['risk_factors'] = risk_factors
        student['risk_level'] = 'critical' if student['final_grade'] < 30 else 'high'
    
    return jsonify({
        'at_risk_students': at_risk,
        'total_at_risk': len(at_risk),
        'threshold': threshold
    }), 200


@analytics_bp.route('/gender_distribution', methods=['GET'])
@jwt_required()
@handle_exceptions
def gender_distribution():
    """
    Get gender distribution statistics.
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Gender distribution
    """
    pipeline = [
        {
            '$group': {
                '_id': '$gender',
                'count': {'$sum': 1},
                'average_grade': {'$avg': '$final_grade'},
                'average_study_time': {'$avg': '$study_time'},
                'average_absences': {'$avg': '$absences'}
            }
        },
        {
            '$sort': {'count': -1}
        }
    ]
    
    results = list(mongo.db.students.aggregate(pipeline))
    
    # Calculate total and percentages
    total_students = sum(r['count'] for r in results)
    
    distribution = []
    for result in results:
        distribution.append({
            'gender': result['_id'],
            'count': result['count'],
            'percentage': round((result['count'] / total_students * 100), 2) if total_students > 0 else 0,
            'average_grade': round(result['average_grade'], 2),
            'average_study_time': round(result['average_study_time'], 2),
            'average_absences': round(result['average_absences'], 2)
        })
    
    return jsonify({
        'gender_distribution': distribution,
        'total_students': total_students
    }), 200


@analytics_bp.route('/performance_by_support', methods=['GET'])
@jwt_required()
@handle_exceptions
def performance_by_support():
    """
    Analyze performance based on parental support levels.
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Performance statistics by parental support
    """
    pipeline = [
        {
            '$group': {
                '_id': '$parental_support',
                'count': {'$sum': 1},
                'average_grade': {'$avg': '$final_grade'},
                'pass_rate': {
                    '$avg': {
                        '$cond': [{'$gte': ['$final_grade', 40]}, 1, 0]
                    }
                }
            }
        },
        {
            '$sort': {'average_grade': -1}
        }
    ]
    
    results = list(mongo.db.students.aggregate(pipeline))
    
    support_stats = []
    for result in results:
        support_stats.append({
            'parental_support': result['_id'],
            'count': result['count'],
            'average_grade': round(result['average_grade'], 2),
            'pass_rate': round(result['pass_rate'] * 100, 2)
        })
    
    return jsonify({
        'performance_by_support': support_stats
    }), 200


@analytics_bp.route('/internet_access_impact', methods=['GET'])
@jwt_required()
@handle_exceptions
def internet_access_impact():
    """
    Analyze impact of internet access on performance.
    ---
    tags:
      - Analytics
    security:
      - Bearer: []
    responses:
      200:
        description: Performance statistics by internet access
    """
    pipeline = [
        {
            '$group': {
                '_id': '$internet_access',
                'count': {'$sum': 1},
                'average_grade': {'$avg': '$final_grade'},
                'average_study_time': {'$avg': '$study_time'},
                'pass_rate': {
                    '$avg': {
                        '$cond': [{'$gte': ['$final_grade', 40]}, 1, 0]
                    }
                }
            }
        }
    ]
    
    results = list(mongo.db.students.aggregate(pipeline))
    
    access_stats = []
    for result in results:
        access_stats.append({
            'has_internet_access': result['_id'],
            'count': result['count'],
            'average_grade': round(result['average_grade'], 2),
            'average_study_time': round(result['average_study_time'], 2),
            'pass_rate': round(result['pass_rate'] * 100, 2)
        })
    
    return jsonify({
        'internet_access_impact': access_stats
    }), 200


@analytics_bp.route('/class_summary', methods=['GET'])
@jwt_required()
@role_required('teacher')
@handle_exceptions
def class_summary():
    """
    Comprehensive class performance overview (Teacher only).
    ---
    tags:
      - Analytics
      - Teacher
    security:
      - Bearer: []
    responses:
      200:
        description: Comprehensive class statistics
      403:
        description: Forbidden - Teacher access required
    """
    # Overall statistics
    pipeline_overall = [
        {
            '$group': {
                '_id': None,
                'total_students': {'$sum': 1},
                'average_grade': {'$avg': '$final_grade'},
                'average_study_time': {'$avg': '$study_time'},
                'average_absences': {'$avg': '$absences'},
                'pass_count': {
                    '$sum': {
                        '$cond': [{'$gte': ['$final_grade', 40]}, 1, 0]
                    }
                },
                'at_risk_count': {
                    '$sum': {
                        '$cond': [{'$lt': ['$final_grade', 40]}, 1, 0]
                    }
                }
            }
        }
    ]
    
    overall = list(mongo.db.students.aggregate(pipeline_overall))
    
    if not overall:
        return jsonify({
            'error': 'No data available',
            'message': 'No students found in database'
        }), 404
    
    stats = overall[0]
    total = stats['total_students']
    
    # Grade distribution
    grade_ranges = [
        {'range': 'A (90-100)', 'min': 90, 'max': 100},
        {'range': 'B (80-89)', 'min': 80, 'max': 89},
        {'range': 'C (70-79)', 'min': 70, 'max': 79},
        {'range': 'D (60-69)', 'min': 60, 'max': 69},
        {'range': 'E (40-59)', 'min': 40, 'max': 59},
        {'range': 'F (0-39)', 'min': 0, 'max': 39}
    ]
    
    grade_distribution = []
    for grade_range in grade_ranges:
        count = mongo.db.students.count_documents({
            'final_grade': {
                '$gte': grade_range['min'],
                '$lte': grade_range['max']
            }
        })
        grade_distribution.append({
            'grade': grade_range['range'],
            'count': count,
            'percentage': round((count / total * 100), 2) if total > 0 else 0
        })
    
    return jsonify({
        'class_summary': {
            'total_students': total,
            'average_grade': round(stats['average_grade'], 2),
            'average_study_time': round(stats['average_study_time'], 2),
            'average_absences': round(stats['average_absences'], 2),
            'pass_rate': round((stats['pass_count'] / total * 100), 2) if total > 0 else 0,
            'at_risk_count': stats['at_risk_count'],
            'grade_distribution': grade_distribution
        }
    }), 200
