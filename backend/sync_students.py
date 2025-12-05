
from pymongo import MongoClient
from datetime import datetime
import os

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')

def sync_students():
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    
    users_collection = db.users
    students_collection = db.students
    
    # Find all users with role 'student'
    student_users = list(users_collection.find({'role': 'student'}))
    print(f"Found {len(student_users)} users with role 'student'.")
    
    synced_count = 0
    
    for user in student_users:
        if 'student_id' not in user:
            print(f"Skipping user {user['username']} (no student_id)")
            continue
            
        student_id = user['student_id']
        
        # Check if exists in students collection
        existing_student = students_collection.find_one({'student_id': student_id})
        
        if not existing_student:
            print(f"Syncing missing student: {user['username']} ({student_id})")
            
            student_doc = {
                'student_id': student_id,
                'name': user.get('full_name', user['username']),
                'age': 0,
                'gender': 'Other',
                'study_time': 0,
                'absences': 0,
                'parental_support': 'medium',
                'internet_access': False,
                'final_grade': 0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            students_collection.insert_one(student_doc)
            synced_count += 1
        else:
            print(f"Student {student_id} already exists.")
            
    print(f"Sync complete. Synced {synced_count} students.")

if __name__ == "__main__":
    sync_students()
