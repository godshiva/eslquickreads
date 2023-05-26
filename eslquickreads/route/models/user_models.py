from eslquickreads import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# user loader to load user to login
@login_manager.user_loader
def load_user(user_email):
    """Required for session management in Flask-Login requirement, We are storing emails of every user in session to
     satisfy session management unique identity. Because email is an unique identity in our system for every user we
     are using it. Make sure we should add email validation in all the registration form's in case if we add another
     user, and add the same user login identity in load_user too."""
    if Users.query.filter_by(email=user_email).first():
        return Users.query.filter_by(email=user_email).first()
    elif Developer.query.filter_by(email=user_email).first():
        return Developer.query.filter_by(email=user_email).first()


# Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_img = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False)
    lesson_history = db.relationship('LessonsHistory', backref='user', lazy=True)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
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
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_img = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
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
