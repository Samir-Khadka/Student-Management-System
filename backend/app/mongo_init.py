"""
Flask application factory module.
Creates and configures the Flask application instance.
"""
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
import logging
from datetime import datetime
from config.config import get_config
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

mongo_client = None
mongo_db = None

jwt = JWTManager()


class MongoWrapper:
    """Wrapper class to mimic Flask-PyMongo interface"""
    def __init__(self):
        self.db = None
        self.cx = None
    
    def init_app(self, app):
        """Initialize MongoDB connection"""
        print(f"\n{'='*60}")
        print("INITIALIZING MONGODB CONNECTION...")
        print(f"{'='*60}")
        
        try:
            uri = app.config.get('MONGO_URI')
            db_name = app.config.get('MONGODB_DB', 'student_management')
            
            print(f"MongoDB URI: {uri}")
            print(f"Database name: {db_name}")
            
            # Create client
            print("Creating MongoClient...")
            self.cx = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # FORCE CONNECTION by pinging
            print("Testing connection with ping...")
            self.cx.admin.command('ping')
            print("✓ MongoDB ping successful!")
            
            # Set database
            self.db = self.cx[db_name]
            print(f"✓ MongoDB initialized: database='{db_name}'")
            print(f"{'='*60}\n")
            
            app.logger.info(f"MongoDB successfully connected to database: {db_name}")
            
        except Exception as e:
            print(f"\n{'!'*60}")
            print(f"✗ MONGODB CONNECTION FAILED!")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"{'!'*60}\n")
            
            app.logger.error(f"MongoDB connection failed: {str(e)}")
            self.db = None
            self.cx = None
            # RAISE THE ERROR - don't let app start with broken DB
            raise Exception(f"MongoDB connection failed: {str(e)}")


mongo = MongoWrapper()
