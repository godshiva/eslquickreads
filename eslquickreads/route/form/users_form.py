from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from eslquickreads.route.models.user_models import Developer, Users


class RegisterForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        # Normalize email to lowercase for case-insensitive matching
        normalized_email = email.data.lower() if email.data else None
        
        # Check if the email exists directly (case-insensitive search)
        # First check normalized against stored values
        dev = Developer.query.filter_by(email=normalized_email).first()
        user = Users.query.filter_by(email=normalized_email).first()
        
        # If not found, also try original email for legacy data that might have mixed case
        if not (user or dev) and normalized_email != email.data:
            dev = Developer.query.filter_by(email=email.data).first()
            user = Users.query.filter_by(email=email.data).first()
        
        # If we're in the transition period, also check by hashed email
        if not (user or dev):
            from eslquickreads.route.models.user_models import hash_email
            # hash_email already handles case normalization
            email_hash_value = hash_email(email.data)
            dev = Developer.query.filter_by(email_hash=email_hash_value).first()
            user = Users.query.filter_by(email_hash=email_hash_value).first()
            
        if user or dev:
            raise ValidationError('Email already exists in our system, please try another one')


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Sign In')


class EmailPasswordForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired()])
    submit = SubmitField('Send Reset Email')


class PasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Update Pass')
