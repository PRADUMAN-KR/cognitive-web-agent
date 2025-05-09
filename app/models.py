from . import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    datetime_registered = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one user can have many web bots
    webbots = db.relationship('WebBot', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    

class WebBot(db.Model):
    __tablename__ = 'webbots'

    id = db.Column(db.Integer, primary_key=True)
    bot_name = db.Column(db.String(64), unique=True, nullable=False)
    website_url = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<WebBot {self.bot_name}>'
