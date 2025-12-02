"""
Swagger/OpenAPI configuration for Flasgger.
"""

# Swagger UI configuration
SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

# Swagger template with JWT authentication
SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Student Academic Performance Management System API",
        "description": "REST API for managing student academic performance data with analytics and predictions. Built for COM661 CW1 assignment.",
        "contact": {
            "name": "API Support",
            "email": "support@studentmanagement.com"
        },
        "version": "1.0.0"
    },
    "host": "localhost:5001",
    "basePath": "/",
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
        }
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User authentication and registration endpoints"
        },
        {
            "name": "Students",
            "description": "Student CRUD operations"
        },
        {
            "name": "Analytics",
            "description": "Statistical analysis and insights"
        },
        {
            "name": "Teacher",
            "description": "Teacher-specific endpoints"
        },
        {
            "name": "Student Profile",
            "description": "Student profile management"
        }
    ],
    "definitions": {
        "Student": {
            "type": "object",
            "required": ["student_id", "name", "age", "gender", "study_time", "absences", "parental_support", "internet_access", "final_grade"],
            "properties": {
                "student_id": {
                    "type": "string",
                    "example": "STU001"
                },
                "name": {
                    "type": "string",
                    "example": "John Doe"
                },
                "age": {
                    "type": "integer",
                    "example": 18
                },
                "gender": {
                    "type": "string",
                    "enum": ["male", "female", "other"],
                    "example": "male"
                },
                "study_time": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 20,
                    "example": 10
                },
                "absences": {
                    "type": "integer",
                    "minimum": 0,
                    "example": 3
                },
                "parental_support": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "example": "high"
                },
                "internet_access": {
                    "type": "boolean",
                    "example": True
                },
                "final_grade": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "example": 75
                },
                "attendance_log": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            }
        },
        "User": {
            "type": "object",
            "required": ["username", "password", "email", "role"],
            "properties": {
                "username": {
                    "type": "string",
                    "example": "johndoe"
                },
                "password": {
                    "type": "string",
                    "example": "password123"
                },
                "email": {
                    "type": "string",
                    "example": "john@example.com"
                },
                "role": {
                    "type": "string",
                    "enum": ["student", "teacher", "admin"],
                    "example": "student"
                },
                "full_name": {
                    "type": "string",
                    "example": "John Doe"
                },
                "student_id": {
                    "type": "string",
                    "example": "STU001"
                }
            }
        },
        "Error": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string"
                },
                "message": {
                    "type": "string"
                }
            }
        }
    }
}
