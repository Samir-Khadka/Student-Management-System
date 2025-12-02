"""
Test analytics endpoints.
"""
import pytest


def test_average_grade(client, auth_headers):
    """Test average grade calculation."""
    students = [
        {
            'student_id': 'STU020',
            'name': 'Student A',
            'age': 18,
            'gender': 'male',
            'study_time': 10,
            'absences': 2,
            'parental_support': 'high',
            'internet_access': True,
            'final_grade': 80
        },
        {
            'student_id': 'STU021',
            'name': 'Student B',
            'age': 17,
            'gender': 'female',
            'study_time': 12,
            'absences': 1,
            'parental_support': 'medium',
            'internet_access': True,
            'final_grade': 90
        }
    ]
    
    for student in students:
        client.post('/api/students/', json=student, headers=auth_headers)
    
    response = client.get('/api/analytics/average_grade', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'average_grade' in data
    assert data['total_students'] >= 2


def test_at_risk_students(client, auth_headers):
    """Test identifying at-risk students."""
    students = [
        {
            'student_id': 'STU030',
            'name': 'High Performer',
            'age': 18,
            'gender': 'male',
            'study_time': 15,
            'absences': 0,
            'parental_support': 'high',
            'internet_access': True,
            'final_grade': 85
        },
        {
            'student_id': 'STU031',
            'name': 'At Risk Student',
            'age': 17,
            'gender': 'female',
            'study_time': 3,
            'absences': 15,
            'parental_support': 'low',
            'internet_access': False,
            'final_grade': 30
        }
    ]
    
    for student in students:
        client.post('/api/students/', json=student, headers=auth_headers)
    
    response = client.get('/api/analytics/at_risk_students', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'at_risk_students' in data
    assert data['total_at_risk'] >= 1
    # Verify at-risk student is in the list
    at_risk_ids = [s['student_id'] for s in data['at_risk_students']]
    assert 'STU031' in at_risk_ids


def test_gender_distribution(client, auth_headers):
    """Test gender distribution statistics."""
    # Create students with different genders
    students = [
        {
            'student_id': 'STU040',
            'name': 'Male Student 1',
            'age': 18,
            'gender': 'male',
            'study_time': 10,
            'absences': 2,
            'parental_support': 'high',
            'internet_access': True,
            'final_grade': 75
        },
        {
            'student_id': 'STU041',
            'name': 'Female Student 1',
            'age': 17,
            'gender': 'female',
            'study_time': 12,
            'absences': 1,
            'parental_support': 'medium',
            'internet_access': True,
            'final_grade': 80
        },
        {
            'student_id': 'STU042',
            'name': 'Male Student 2',
            'age': 19,
            'gender': 'male',
            'study_time': 8,
            'absences': 5,
            'parental_support': 'low',
            'internet_access': False,
            'final_grade': 65
        }
    ]
    
    for student in students:
        client.post('/api/students/', json=student, headers=auth_headers)
    
    response = client.get('/api/analytics/gender_distribution', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'gender_distribution' in data
    assert data['total_students'] >= 3
    
    # Verify distribution structure
    for gender_data in data['gender_distribution']:
        assert 'gender' in gender_data
        assert 'count' in gender_data
        assert 'percentage' in gender_data
        assert 'average_grade' in gender_data


def test_performance_by_support(client, auth_headers):
    """Test performance analysis by parental support."""
    # Create students with different support levels
    students = [
        {
            'student_id': 'STU050',
            'name': 'High Support Student',
            'age': 18,
            'gender': 'male',
            'study_time': 12,
            'absences': 1,
            'parental_support': 'high',
            'internet_access': True,
            'final_grade': 85
        },
        {
            'student_id': 'STU051',
            'name': 'Low Support Student',
            'age': 17,
            'gender': 'female',
            'study_time': 6,
            'absences': 8,
            'parental_support': 'low',
            'internet_access': False,
            'final_grade': 45
        }
    ]
    
    for student in students:
        client.post('/api/students/', json=student, headers=auth_headers)
    
    response = client.get('/api/analytics/performance_by_support', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'performance_by_support' in data
    assert len(data['performance_by_support']) > 0


def test_internet_access_impact(client, auth_headers):
    """Test internet access impact analysis."""
    # Create students with and without internet
    students = [
        {
            'student_id': 'STU060',
            'name': 'With Internet',
            'age': 18,
            'gender': 'male',
            'study_time': 12,
            'absences': 2,
            'parental_support': 'high',
            'internet_access': True,
            'final_grade': 80
        },
        {
            'student_id': 'STU061',
            'name': 'Without Internet',
            'age': 17,
            'gender': 'female',
            'study_time': 10,
            'absences': 3,
            'parental_support': 'medium',
            'internet_access': False,
            'final_grade': 70
        }
    ]
    
    for student in students:
        client.post('/api/students/', json=student, headers=auth_headers)
    
    response = client.get('/api/analytics/internet_access_impact', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'internet_access_impact' in data


def test_class_summary_teacher_access(client):
    """Test class summary requires teacher role."""
    # Register and login as teacher
    teacher_data = {
        'username': 'teacher1',
        'password': 'password123',
        'email': 'teacher1@test.com',
        'role': 'teacher',
        'full_name': 'Teacher One'
    }
    client.post('/api/auth/register', json=teacher_data)
    
    login_response = client.post('/api/auth/login', json={
        'username': 'teacher1',
        'password': 'password123'
    })
    token = login_response.get_json()['access_token']
    teacher_headers = {'Authorization': f'Bearer {token}'}
    
    # Access class summary
    response = client.get('/api/analytics/class_summary', headers=teacher_headers)
    
    assert response.status_code in [200, 404]


def test_class_summary_student_forbidden(client):
    """Test class summary forbidden for students."""
    student_data = {
        'username': 'student1',
        'password': 'password123',
        'email': 'student1@test.com',
        'role': 'student',
        'full_name': 'Student One',
        'student_id': 'STU070'
    }
    client.post('/api/auth/register', json=student_data)
    
    login_response = client.post('/api/auth/login', json={
        'username': 'student1',
        'password': 'password123'
    })
    token = login_response.get_json()['access_token']
    student_headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/analytics/class_summary', headers=student_headers)
    
    # Should be forbidden
    assert response.status_code == 403
