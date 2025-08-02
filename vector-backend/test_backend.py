#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""

from flask import Flask
from models import db, ChatSession, FollowUp
import os
import sys

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chat_sessions.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("[INFO] Testing database connection...")
        
        # Test database query
        session_count = ChatSession.query.count()
        print(f"[OK] Database accessible - {session_count} sessions found")
        
        # Test cache import (should work without Redis)
        try:
            from cache_config import cache
            print("[OK] Cache module imported successfully (Redis optional)")
        except Exception as e:
            print(f"[ERROR] Cache import failed: {e}")
            return False
        
        # Test other imports
        try:
            import prompt_checker
            print("[OK] Prompt checker imported")
        except Exception as e:
            print(f"[WARNING] Prompt checker failed: {e}")
        
        try:
            import google_search
            print("[OK] Google search module imported")
        except Exception as e:
            print(f"[WARNING] Google search failed: {e}")
        
        print("[OK] Basic functionality test passed!")
        return True

if __name__ == "__main__":
    if test_basic_functionality():
        print("\n[SUCCESS] Backend is ready to run!")
        print("To start the server, run: python app.py")
    else:
        print("\n[ERROR] Backend has issues")
        sys.exit(1)