#!/usr/bin/env python3
"""
Simple database initialization script that doesn't require Redis.
"""

from flask import Flask
from models import db, User, ChatSession, FollowUp
import os

def init_database():
    """Initialize the database with tables"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chat_sessions.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("[INFO] Creating database tables...")
        db.create_all()
        
        # Add the new columns manually since we can't run migrations easily
        try:
            # Check if new columns exist, if not add them
            db.engine.execute("ALTER TABLE chat_session ADD COLUMN completed_at DATETIME")
            print("[INFO] Added completed_at column")
        except Exception:
            print("[INFO] completed_at column already exists")
            
        try:
            db.engine.execute("ALTER TABLE chat_session ADD COLUMN final_answer TEXT")
            print("[INFO] Added final_answer column")
        except Exception:
            print("[INFO] final_answer column already exists")
            
        try:
            db.engine.execute("ALTER TABLE chat_session ADD COLUMN status VARCHAR(50) DEFAULT 'pending'")
            print("[INFO] Added status column")
        except Exception:
            print("[INFO] status column already exists")
            
        try:
            db.engine.execute("ALTER TABLE chat_session ADD COLUMN user_id VARCHAR")
            print("[INFO] Added user_id column")
        except Exception:
            print("[INFO] user_id column already exists")
        
        print("[OK] Database initialization complete!")

if __name__ == "__main__":
    init_database()