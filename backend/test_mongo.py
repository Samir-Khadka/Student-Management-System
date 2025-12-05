#!/usr/bin/env python
"""Test MongoDB connection"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables
load_dotenv()

# Get MongoDB URI
mongo_uri = os.getenv('MONGO_URI')
print(f"MongoDB URI: {mongo_uri[:60]}...")

try:
    # Create client
    print("\nCreating MongoDB client...")
    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test connection
    print("Testing connection with ping...")
    client.admin.command('ping')
    print("✓ MongoDB connection successful!")
    
    # List databases
    print("\nAvailable databases:")
    for db_name in client.list_database_names():
        print(f"  - {db_name}")
    
    # Get student_management database
    db = client['student_management']
    print(f"\nConnected to database: student_management")
    
    # List collections
    print("Collections:")
    for coll_name in db.list_collection_names():
        print(f"  - {coll_name}")
    
    # Check if users collection exists and has documents
    if 'users' in db.list_collection_names():
        user_count = db.users.count_documents({})
        print(f"\nUsers collection has {user_count} documents")
        if user_count > 0:
            print("Sample user:")
            user = db.users.find_one()
            print(f"  - Username: {user.get('username', 'N/A')}")
            print(f"  - Role: {user.get('role', 'N/A')}")
    
except ConnectionFailure as e:
    print(f"✗ Connection failed: {e}")
except ServerSelectionTimeoutError as e:
    print(f"✗ Server selection timeout: {e}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
