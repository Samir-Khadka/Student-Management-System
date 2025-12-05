#!/usr/bin/env python
"""Check what configuration the backend is using"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

print("=== Environment Variables ===")
print(f"MONGO_URI: {os.getenv('MONGO_URI')}")
print(f"APP_PORT: {os.getenv('APP_PORT')}")
print(f"CORS_ORIGINS: {os.getenv('CORS_ORIGINS')}")
print()

# Now test what create_app sees
from app import create_app
app = create_app()

print("=== App Configuration ===")
print(f"MONGO_URI: {app.config.get('MONGO_URI')}")
print(f"DEBUG: {app.config.get('DEBUG')}")
print(f"CORS_ORIGINS: {app.config.get('CORS_ORIGINS')}")
print()

# Check mongo object
from app import mongo
print("=== MongoDB Connection ===")
print(f"mongo.db: {mongo.db}")
print(f"mongo.cx: {mongo.cx}")

if mongo.db is not None:
    print(f"Database name: {mongo.db.name}")
    try:
        # Try to ping
        mongo.cx.admin.command('ping')
        print("✓ MongoDB ping successful!")
    except Exception as e:
        print(f"✗ MongoDB ping failed: {e}")
else:
    print("✗ MongoDB database is None!")
