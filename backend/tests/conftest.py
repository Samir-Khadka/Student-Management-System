"""
Pytest configuration and fixtures.
"""
import pytest
from app import create_app, mongo


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    app.config['TESTING'] = True
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/student_management_test'
    
    yield app
    
    with app.app_context():
        try:
            mongo.db.students.delete_many({})
            mongo.db.users.delete_many({})
        except Exception:
            pass


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create authenticated test user and return JWT token headers."""
    # Register admin user
    register_data = {
        'username': 'testadmin',
        'password': 'password123',
        'email': 'admin@test.com',
        'role': 'admin',
        'full_name': 'Test Admin'
    }
    client.post('/api/auth/register', json=register_data)
    
    # Login
    login_data = {
        'username': 'testadmin',
        'password': 'password123'
    }
    response = client.post('/api/auth/login', json=login_data)
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_student():
    """Sample student data for testing."""
    return {
        'student_id': 'STU001',
        'name': 'John Doe',
        'age': 18,
        'gender': 'male',
        'study_time': 10,
        'absences': 3,
        'parental_support': 'high',
        'internet_access': True,
        'final_grade': 75
    }
