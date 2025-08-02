from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    google_id = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to chat sessions
    sessions = db.relationship("ChatSession", backref="user", lazy=True)

class ChatSession(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    initial_question = db.Column(db.Text, nullable=False)
    short_answer = db.Column(db.Text, nullable=True)
    final_answer = db.Column(db.Text, nullable=True)
    thread_id = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='pending')  # pending, in_progress, completed, failed
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=True)  # nullable for existing sessions

    followups = db.relationship("FollowUp", backref="session", lazy=True)


class FollowUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String, db.ForeignKey('chat_session.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
