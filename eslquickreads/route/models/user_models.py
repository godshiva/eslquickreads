from eslquickreads import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib


# user loader to load user to login
@login_manager.user_loader
def load_user(user_identifier):
    """Required for session management in Flask-Login requirement. 
    During the transition period, this can handle both email and hashed email identifiers.
    
    First, we try to find a user by their plain email (old method).
    If not found, we check if the identifier might be a hashed email.
    """
    # Try to find using plain email (old method)
    user = Users.query.filter_by(email=user_identifier).first()
    if user:
        return user
    
    dev = Developer.query.filter_by(email=user_identifier).first()
    if dev:
        return dev
        
    # If not found, check if it's a hashed email (new method)
    user = Users.query.filter_by(email_hash=user_identifier).first()
    if user:
        return user
    
    dev = Developer.query.filter_by(email_hash=user_identifier).first()
    if dev:
        return dev
        
    # No user found with either method
    return None


# Helper function to hash email with pepper
def hash_email(email):
    """Hash an email address with pepper for secure storage"""
    if not email:
        return None
    
    # Convert email to lowercase to ensure case-insensitive matching
    # Emails are by standard case-insensitive, so user@example.com and User@Example.com 
    # should generate the same hash
    normalized_email = email.lower()
    
    # Get the pepper from app config
    email_pepper = app.config.get('USER_PEPPER', '')
    
    # Create a hash using the pepper
    email_hash = hashlib.sha256((normalized_email + email_pepper).encode()).hexdigest()
    
    return email_hash

# Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Keep original for transition
    email_hash = db.Column(db.String(64), unique=True, nullable=True)  # New hashed email field
    profile_img = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False)
    lesson_history = db.relationship('LessonsHistory', backref='user', lazy=True)
    
    def update_email_hash(self):
        """Update the hashed email field based on the plain email"""
        if self.email:
            self.email_hash = hash_email(self.email)
            return True
        return False

    def get_id(self):
        """Return the identifier to satisfy Flask-Login's requirements.
        
        During transition: If email_hash is available, use it; otherwise, fall back to email.
        This allows for a gradual transition to the new system.
        """
        if self.email_hash:
            return self.email_hash
        return self.email

    def get_reset_token(self, expire_sec=1800):
        """For generating tokens for forgot password and many more."""
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({'users': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """for verifying tokens for forgot password and many more"""
        s = Serializer(app.config['SECRET_KEY'])
        try:
            users_id = s.loads(token)['users']
        except:
            return None
        return Users.query.filter_by(email=users_id).first()


# Developer Model
class Developer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Keep original for transition
    email_hash = db.Column(db.String(64), unique=True, nullable=True)  # New hashed email field
    profile_img = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False)
    
    def update_email_hash(self):
        """Update the hashed email field based on the plain email"""
        if self.email:
            self.email_hash = hash_email(self.email)
            return True
        return False

    def get_id(self):
        """Return the identifier to satisfy Flask-Login's requirements.
        
        During transition: If email_hash is available, use it; otherwise, fall back to email.
        This allows for a gradual transition to the new system.
        """
        if self.email_hash:
            return self.email_hash
        return self.email

    def get_reset_token(self, expire_sec=1800):
        """For generating tokens for forgot password and many more."""
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({'developer': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """for verifying tokens for forgot password and many more"""
        s = Serializer(app.config['SECRET_KEY'])
        try:
            users_id = s.loads(token)['developer']
        except:
            return None
        return Developer.query.filter_by(email=users_id).first()
