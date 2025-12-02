"""
Test authentication endpoints.
"""
import pytest


def test_register_success(client):
    """Test successful user registration."""
    data = {
        'username': 'newuser',
        'password': 'password123',
        'email': 'newuser@test.com',
        'role': 'student',
        'full_name': 'New User',
        'student_id': 'STU999'
    }
    response = client.post('/api/auth/register', json=data)
    
    assert response.status_code == 201
    assert 'user_id' in response.get_json()


def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    data = {
        'username': 'testuser',
        'password': 'password123',
        'email': 'user1@test.com',
        'role': 'student',
        'student_id': 'STU100'
    }
    # First registration
    client.post('/api/auth/register', json=data)
    
    # Try duplicate
    data['email'] = 'user2@test.com'
    response = client.post('/api/auth/register', json=data)
    
    assert response.status_code == 409


def test_register_missing_student_id(client):
    """Test student registration without student_id."""
    data = {
        'username': 'student1',
        'password': 'password123',
        'email': 'student@test.com',
        'role': 'student',
        'full_name': 'Student One'
    }
    response = client.post('/api/auth/register', json=data)
    
    assert response.status_code == 400


def test_login_success(client):
    """Test successful login."""
    # Register user first
    register_data = {
        'username': 'loginuser',
        'password': 'password123',
        'email': 'login@test.com',
        'role': 'teacher',
        'full_name': 'Login User'
    }
    client.post('/api/auth/register', json=register_data)
    
    # Login
    login_data = {
        'username': 'loginuser',
        'password': 'password123'
    }
    response = client.post('/api/auth/login', json=login_data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['role'] == 'teacher'


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    data = {
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }
    response = client.post('/api/auth/login', json=data)
    
    assert response.status_code == 401


def test_refresh_token(client):
    """Test token refresh."""
    # Register and login
    register_data = {
        'username': 'refreshuser',
        'password': 'password123',
        'email': 'refresh@test.com',
        'role': 'admin',
        'full_name': 'Refresh User'
    }
    client.post('/api/auth/register', json=register_data)
    
    login_response = client.post('/api/auth/login', json={
        'username': 'refreshuser',
        'password': 'password123'
    })
    refresh_token = login_response.get_json()['refresh_token']
    
    # Refresh
    headers = {'Authorization': f'Bearer {refresh_token}'}
    response = client.post('/api/auth/refresh', headers=headers)
    
    assert response.status_code == 200
    assert 'access_token' in response.get_json()


def test_get_current_user(client, auth_headers):
    """Test getting current user profile."""
    response = client.get('/api/auth/me', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testadmin'
    assert data['role'] == 'admin'


def test_unauthorized_access(client):
    """Test accessing protected endpoint without token."""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401
