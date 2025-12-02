"""
Student model with schema and validation.
Defines the structure for student records in MongoDB.
"""
from marshmallow import Schema, fields, validate, ValidationError


class StudentSchema(Schema):
    """Schema for student validation and serialization."""
    student_id = fields.Str(required=True, validate=validate.Length(min=1))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=5, max=100))
    gender = fields.Str(required=True, validate=validate.OneOf(['Male', 'Female', 'Other']))
    study_time = fields.Int(required=True, validate=validate.Range(min=0, max=168))
    absences = fields.Int(required=True, validate=validate.Range(min=0))
    parental_support = fields.Str(required=True, validate=validate.OneOf(['low', 'medium', 'high']))
    internet_access = fields.Bool(required=True)
    final_grade = fields.Int(required=True, validate=validate.Range(min=0, max=100))
    attendance_log = fields.List(fields.Dict(), required=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class StudentUpdateSchema(Schema):
    """Schema for updating student - all fields optional."""
    student_id = fields.Str(validate=validate.Length(min=1))
    name = fields.Str(validate=validate.Length(min=1, max=100))
    age = fields.Int(validate=validate.Range(min=5, max=100))
    gender = fields.Str(validate=validate.OneOf(['Male', 'Female', 'Other']))
    study_time = fields.Int(validate=validate.Range(min=0, max=168))
    absences = fields.Int(validate=validate.Range(min=0))
    parental_support = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))
    internet_access = fields.Bool()
    final_grade = fields.Int(validate=validate.Range(min=0, max=100))
    attendance_log = fields.List(fields.Dict())


def validate_student_data(data, partial=False):
    """Validate student data against schema."""
    if partial:
        schema = StudentUpdateSchema()
    else:
        schema = StudentSchema()
    
    return schema.load(data)


def serialize_student(student):
    """Serialize student document for JSON response."""
    if student is None:
        return None
    
    student['_id'] = str(student['_id'])
    return student


def predict_student_performance(student):
    """Predict if student will pass or fail based on final grade."""
    grade = student.get('final_grade', 0)
    prediction = 'pass' if grade >= 40 else 'fail'
    confidence = abs(grade - 40) / 60
    
    return {
        'student_id': student.get('student_id'),
        'name': student.get('name'),
        'final_grade': grade,
        'prediction': prediction,
        'confidence': round(confidence, 2),
        'risk_level': 'high' if grade < 40 else 'low' if grade < 60 else 'none'
    }
