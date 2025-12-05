"""
Direct test of MongoDB connection to diagnose the issue
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

# Load env
load_dotenv()

print("="*60)
print("MONGODB CONNECTION TEST")
print("="*60)

# Get config
mongo_uri = os.getenv('MONGO_URI')
print(f"\n1. MONGO_URI from .env: {mongo_uri}")

# Try to connect
print("\n2. Creating MongoClient...")
try:
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    print("   ✓ MongoClient created")
    
    print("\n3. Testing connection with ping...")
    result = client.admin.command('ping')
    print(f"   ✓ Ping successful: {result}")
    
    print("\n4. Getting database reference...")
    db = client['student_management']
    print(f"   ✓ Database object: {db}")
    
    print("\n5. Checking collections...")
    collections = db.list_collection_names()
    print(f"   Collections: {collections}")
    
    print("\n6. Checking users collection...")
    users = db.users
    count = users.count_documents({})
    print(f"   Users count: {count}")
    
    if count > 0:
        print("\n7. Sample user:")
        user = users.find_one()
        print(f"   Username: {user.get('username')}")
        print(f"   Role: {user.get('role')}")
    
    print(f"\n{'='*60}")
    print("✓ ALL TESTS PASSED!")
    print(f"{'='*60}\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
