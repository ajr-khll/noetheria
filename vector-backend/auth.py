"""
Authentication middleware for verifying Google JWT tokens
"""

import os
from functools import wraps
from flask import request, jsonify, g
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from models import User, db


def verify_google_token(token):
    """Verify Google ID token and return user info"""
    try:
        # Verify the token
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not client_id:
            return None
            
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id
        )
        
        # Check issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return None
            
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture', '')
        }
        
    except ValueError:
        # Invalid token
        return None


def get_or_create_user(user_info):
    """Get existing user or create new one"""
    user = User.query.filter_by(google_id=user_info['google_id']).first()
    
    if not user:
        # Create new user
        user = User(
            google_id=user_info['google_id'],
            email=user_info['email'],
            name=user_info['name'],
            picture=user_info['picture']
        )
        db.session.add(user)
        db.session.commit()
        print(f"[AUTH] Created new user: {user_info['email']}")
    else:
        # Update user info in case it changed
        user.email = user_info['email']
        user.name = user_info['name']
        user.picture = user_info['picture']
        db.session.commit()
        
    return user


def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No valid authorization token provided"}), 401
            
        token = auth_header.split(' ')[1]
        
        # Verify token
        user_info = verify_google_token(token)
        if not user_info:
            return jsonify({"error": "Invalid or expired token"}), 401
            
        # Get or create user
        user = get_or_create_user(user_info)
        
        # Store user in g for use in route
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """Decorator for optional authentication (allows both authenticated and guest users)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Initialize as guest user
        g.current_user = None
        
        # Check for auth header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_info = verify_google_token(token)
            
            if user_info:
                user = get_or_create_user(user_info)
                g.current_user = user
                
        return f(*args, **kwargs)
    
    return decorated_function