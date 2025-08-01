from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class ChatSession(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    initial_question = db.Column(db.Text, nullable=False)
    short_answer = db.Column(db.Text, nullable=True)
    thread_id = db.Column(db.String, nullable=True)

    followups = db.relationship("FollowUp", backref="session", lazy=True)


class FollowUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String, db.ForeignKey('chat_session.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
