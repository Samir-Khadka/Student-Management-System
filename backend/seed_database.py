#!/usr/bin/env python
"""
Database seeding script.
Populates MongoDB with dummy data for all APIs to work perfectly.
Run this script after setting up the database: python seed_database.py
"""
import os
import sys
from datetime import datetime, timedelta
import random
from faker import Faker
from pymongo import MongoClient
from app.utils.auth_helper import hash_password

# Configure to use the local environment
sys.path.insert(0, os.path.dirname(__file__))

fake = Faker()


def get_mongo_connection():
    """
    Create MongoDB connection.
    
    Returns:
        MongoDB client and database
    """
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management_dev')
    client = MongoClient(mongo_uri)
    
    # Extract database name from URI or use default
    if '/' in mongo_uri.split('mongodb://')[-1]:
        db_name = mongo_uri.split('/')[-1].split('?')[0]
    else:
        db_name = 'student_management_dev'
    
    db = client[db_name]
    return client, db


def clear_collections(db):
    """
    Clear existing collections to avoid duplicates.
    
    Args:
        db: MongoDB database instance
    """
    print("🧹 Clearing existing collections...")
    db.students.delete_many({})
    db.users.delete_many({})
    print("✓ Collections cleared")


def seed_users(db):
    """
    Seed user accounts with different roles.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        Dictionary of created users
    """
    print("\n👥 Seeding users...")
    
    users_data = [
        {
            'username': 'admin_user',
            'password': hash_password('admin123'),
            'email': 'admin@school.com',
            'role': 'admin',
            'full_name': 'Admin User',
            'is_active': True
        },
        {
            'username': 'teacher_john',
            'password': hash_password('teacher123'),
            'email': 'john.teacher@school.com',
            'role': 'teacher',
            'full_name': 'John Smith',
            'is_active': True
        },
        {
            'username': 'teacher_sarah',
            'password': hash_password('teacher123'),
            'email': 'sarah.teacher@school.com',
            'role': 'teacher',
            'full_name': 'Sarah Wilson',
            'is_active': True
        }
    ]
    
    # Add student users (will link to students)
    for i in range(1, 51):  # 50 students
        student_id = f'S{i:03d}'
        users_data.append({
            'username': f'student_{i:02d}',
            'password': hash_password(f'student{i}123'),
            'email': f'student{i}@school.com',
            'role': 'student',
            'full_name': fake.name(),
            'student_id': student_id,
            'is_active': True
        })
    
    # Add timestamps to all users
    now = datetime.utcnow()
    for user in users_data:
        user['created_at'] = now
        user['updated_at'] = now
    
    # Insert users
    result = db.users.insert_many(users_data)
    print(f"✓ Created {len(result.inserted_ids)} users")
    
    return users_data


def seed_students(db):
    """
    Seed student records with realistic dummy data.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        List of created students
    """
    print("\n📚 Seeding students...")
    
    # Realistic names for students
    first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Evan', 'Fiona', 'George', 'Hannah',
                   'Isaac', 'Julia', 'Kevin', 'Laura', 'Michael', 'Natalie', 'Oliver', 'Penny',
                   'Quinn', 'Ryan', 'Sophia', 'Thomas', 'Uma', 'Victor', 'Wendy', 'Xavier',
                   'Yara', 'Zoe', 'Aarav', 'Bella', 'Caleb', 'Daisy', 'Ethan', 'Freya',
                   'Gavin', 'Harper', 'Ivan', 'Jessica', 'Keith', 'Lily', 'Mason', 'Nina',
                   'Oscar', 'Piper', 'Quinton', 'Rachel', 'Sam', 'Tina', 'Ulysses', 'Violet',
                   'William', 'Xander', 'Yuki', 'Zachary']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Wilson',
                  'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin',
                  'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis',
                  'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright']
    
    genders = ['Male', 'Female', 'Other']
    parental_support_levels = ['low', 'medium', 'high']
    
    students = []
    now = datetime.utcnow()
    
    for i in range(1, 51):  # 50 students
        student_id = f'S{i:03d}'
        
        # Generate realistic data
        age = random.randint(14, 22)
        gender = random.choice(genders)
        study_time = random.randint(0, 40)  # Hours per week
        absences = random.randint(0, 30)
        parental_support = random.choice(parental_support_levels)
        internet_access = random.choice([True, False])
        
        # Generate grade with some correlation to study time and parental support
        base_grade = study_time * 1.5
        if parental_support == 'high':
            base_grade += random.randint(10, 20)
        elif parental_support == 'medium':
            base_grade += random.randint(0, 10)
        
        base_grade -= absences * 0.5
        final_grade = max(0, min(100, int(base_grade + random.randint(-10, 10))))
        
        # Attendance log - simulate daily attendance
        attendance_log = []
        current_date = now - timedelta(days=100)
        for _ in range(100):
            attendance_log.append({
                'date': current_date.isoformat(),
                'present': random.choice([True, False]) if random.random() > 0.1 else True
            })
            current_date += timedelta(days=1)
        
        student = {
            'student_id': student_id,
            'name': f'{random.choice(first_names)} {random.choice(last_names)}',
            'age': age,
            'gender': gender,
            'study_time': study_time,
            'absences': absences,
            'parental_support': parental_support,
            'internet_access': internet_access,
            'final_grade': final_grade,
            'attendance_log': attendance_log,
            'created_at': now - timedelta(days=random.randint(30, 180)),
            'updated_at': now - timedelta(days=random.randint(0, 10))
        }
        
        students.append(student)
    
    # Insert students
    result = db.students.insert_many(students)
    print(f"✓ Created {len(result.inserted_ids)} students")
    
    return students


def print_summary(db):
    """
    Print summary of seeded data.
    
    Args:
        db: MongoDB database instance
    """
    print("\n" + "="*60)
    print("📊 DATABASE SEEDING SUMMARY")
    print("="*60)
    
    # User summary
    total_users = db.users.count_documents({})
    admin_count = db.users.count_documents({'role': 'admin'})
    teacher_count = db.users.count_documents({'role': 'teacher'})
    student_user_count = db.users.count_documents({'role': 'student'})
    
    print(f"\n👥 Users: {total_users}")
    print(f"   ├─ Admin: {admin_count}")
    print(f"   ├─ Teachers: {teacher_count}")
    print(f"   └─ Student accounts: {student_user_count}")
    
    # Student summary
    total_students = db.students.count_documents({})
    male_students = db.students.count_documents({'gender': 'Male'})
    female_students = db.students.count_documents({'gender': 'Female'})
    other_students = db.students.count_documents({'gender': 'Other'})
    
    print(f"\n📚 Students: {total_students}")
    print(f"   ├─ Male: {male_students}")
    print(f"   ├─ Female: {female_students}")
    print(f"   └─ Other: {other_students}")
    
    # Grade statistics
    pipeline = [
        {
            '$group': {
                '_id': None,
                'avg_grade': {'$avg': '$final_grade'},
                'min_grade': {'$min': '$final_grade'},
                'max_grade': {'$max': '$final_grade'},
                'pass_count': {
                    '$sum': {'$cond': [{'$gte': ['$final_grade', 40]}, 1, 0]}
                },
                'fail_count': {
                    '$sum': {'$cond': [{'$lt': ['$final_grade', 40]}, 1, 0]}
                }
            }
        }
    ]
    
    stats = list(db.students.aggregate(pipeline))
    if stats:
        s = stats[0]
        print(f"\n📈 Grade Statistics:")
        print(f"   ├─ Average: {s['avg_grade']:.2f}")
        print(f"   ├─ Range: {s['min_grade']} - {s['max_grade']}")
        print(f"   ├─ Pass count (grade ≥ 40): {s['pass_count']}")
        print(f"   └─ Fail count (grade < 40): {s['fail_count']}")
    
    # Parental support distribution
    pipeline = [
        {'$group': {'_id': '$parental_support', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    
    support_dist = list(db.students.aggregate(pipeline))
    print(f"\n👨‍👩‍👧 Parental Support Distribution:")
    for item in support_dist:
        print(f"   ├─ {item['_id']}: {item['count']}")
    
    # Internet access
    internet_yes = db.students.count_documents({'internet_access': True})
    internet_no = db.students.count_documents({'internet_access': False})
    
    print(f"\n🌐 Internet Access:")
    print(f"   ├─ With access: {internet_yes}")
    print(f"   └─ Without access: {internet_no}")
    
    print("\n" + "="*60)
    print("✅ Database seeding completed successfully!")
    print("="*60)
    
    print("\n🔐 Sample Login Credentials:")
    print("   Admin:")
    print("      Username: admin_user")
    print("      Password: admin123")
    print("\n   Teacher:")
    print("      Username: teacher_john")
    print("      Password: teacher123")
    print("\n   Student:")
    print("      Username: student_01")
    print("      Password: student1123")
    
    print("\n📍 API Endpoints to test:")
    print("   • POST   /api/auth/register")
    print("   • POST   /api/auth/login")
    print("   • GET    /api/auth/me")
    print("   • GET    /api/students/")
    print("   • GET    /api/students/<student_id>")
    print("   • POST   /api/students/")
    print("   • PUT    /api/students/<student_id>")
    print("   • DELETE /api/students/<student_id>")
    print("   • GET    /api/students/predict/<student_id>")
    print("   • GET    /api/analytics/average_grade")
    print("   • GET    /api/analytics/at_risk_students")
    print("   • GET    /api/analytics/gender_distribution")
    print("   • GET    /api/analytics/performance_by_support")
    print("   • GET    /api/analytics/internet_access_impact")
    print("   • GET    /api/analytics/class_summary")
    print()


def main():
    """Main seeding function."""
    print("🌱 Starting Database Seeding...\n")
    
    try:
        # Get MongoDB connection
        client, db = get_mongo_connection()
        print(f"✓ Connected to MongoDB")
        
        # Clear existing data
        clear_collections(db)
        
        # Seed data
        seed_users(db)
        seed_students(db)
        
        # Print summary
        print_summary(db)
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
