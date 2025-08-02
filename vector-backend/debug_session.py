#!/usr/bin/env python3
"""
Debug script to test session creation
"""

from flask import Flask, g
from models import db, User, ChatSession, FollowUp
import os

def test_session_creation():
    """Test session creation without authentication"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///chat_sessions.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("[TEST] Testing session creation...")
        
        # Simulate the session creation logic
        try:
            # Test without user (guest session)
            g.current_user = None
            
            session_data = {
                'initial_question': "Test question", 
                'status': 'in_progress'
            }
            
            # Link to user if authenticated
            if g.current_user:
                session_data['user_id'] = g.current_user.id
                print(f"[SESSION] Creating session for user: {g.current_user.email}")
            else:
                print(f"[SESSION] Creating guest session")
            
            session = ChatSession(**session_data)
            db.session.add(session)
            db.session.commit()
            
            print(f"[OK] Session created successfully: {session.id}")
            
            # Clean up test session
            db.session.delete(session)
            db.session.commit()
            print(f"[OK] Test session cleaned up")
            
        except Exception as e:
            print(f"[ERROR] Session creation failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_session_creation()