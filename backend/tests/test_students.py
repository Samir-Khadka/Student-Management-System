"""
Test student CRUD endpoints.
"""
import pytest


def test_create_student(client, auth_headers, sample_student):
    """Test creating a new student."""
    response = client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['student_id'] == sample_student['student_id']
    assert data['name'] == sample_student['name']


def test_create_student_duplicate(client, auth_headers, sample_student):
    """Test creating duplicate student."""
    # Create first student
    client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    # Try to create duplicate
    response = client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    assert response.status_code == 409


def test_create_student_invalid_data(client, auth_headers):
    """Test creating student with invalid data."""
    invalid_data = {
        'student_id': 'STU002',
        'name': 'Jane Doe',
        'age': 150,  # Invalid age
        'gender': 'invalid',  # Invalid gender
        'study_time': -5,  # Invalid study time
        'absences': 0,
        'parental_support': 'high',
        'internet_access': True,
        'final_grade': 80
    }
    response = client.post('/api/students/', json=invalid_data, headers=auth_headers)
    
    assert response.status_code == 400


def test_get_all_students(client, auth_headers, sample_student):
    """Test getting all students."""
    client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    response = client.get('/api/students/', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0


def test_get_student_by_id(client, auth_headers, sample_student):
    """Test getting a single student by ID."""
    client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    response = client.get(f'/api/students/{sample_student["student_id"]}', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['student_id'] == sample_student['student_id']


def test_get_student_not_found(client, auth_headers):
    """Test getting non-existent student."""
    response = client.get('/api/students/NONEXISTENT', headers=auth_headers)
    
    assert response.status_code == 404


def test_update_student(client, auth_headers, sample_student):
    """Test updating a student."""
    # Create student
    client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    # Update student
    update_data = {
        'final_grade': 85,
        'study_time': 15
    }
    response = client.put(f'/api/students/{sample_student["student_id"]}', 
                         json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['student']['final_grade'] == 85
    assert data['student']['study_time'] == 15


def test_update_student_not_found(client, auth_headers):
    """Test updating non-existent student."""
    update_data = {'final_grade': 90}
    response = client.put('/api/students/NONEXISTENT', 
                         json=update_data, headers=auth_headers)
    
    assert response.status_code == 404


def test_delete_student(client, auth_headers, sample_student):
    """Test deleting a student."""
    # Create student
    client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    # Delete student
    response = client.delete(f'/api/students/{sample_student["student_id"]}', 
                            headers=auth_headers)
    
    assert response.status_code == 200
    
    # Verify deletion
    get_response = client.get(f'/api/students/{sample_student["student_id"]}', 
                              headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_student_not_found(client, auth_headers):
    """Test deleting non-existent student."""
    response = client.delete('/api/students/NONEXISTENT', headers=auth_headers)
    
    assert response.status_code == 404


def test_predict_student_performance(client, auth_headers, sample_student):
    """Test predicting student performance."""
    client.post('/api/students/', json=sample_student, headers=auth_headers)
    
    response = client.get(f'/api/students/predict/{sample_student["student_id"]}', 
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'prediction' in data
    assert data['prediction']['prediction'] in ['pass', 'fail']


def test_filter_students_by_gender(client, auth_headers):
    """Test filtering students by gender."""
    # Create students with different genders
    student1 = {
        'student_id': 'STU010',
        'name': 'Male Student',
        'age': 18,
        'gender': 'male',
        'study_time': 10,
        'absences': 2,
        'parental_support': 'high',
        'internet_access': True,
        'final_grade': 75
    }
    student2 = {
        'student_id': 'STU011',
        'name': 'Female Student',
        'age': 17,
        'gender': 'female',
        'study_time': 12,
        'absences': 1,
        'parental_support': 'medium',
        'internet_access': True,
        'final_grade': 80
    }
    
    client.post('/api/students/', json=student1, headers=auth_headers)
    client.post('/api/students/', json=student2, headers=auth_headers)
    
    # Filter by male
    response = client.get('/api/students/?gender=male', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert all(s['gender'] == 'male' for s in data)


def test_unauthorized_access_students(client):
    """Test accessing students endpoint without authentication."""
    response = client.get('/api/students/')
    
    assert response.status_code == 401
