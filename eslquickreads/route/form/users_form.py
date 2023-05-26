from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from eslquickreads.route.models.user_models import Developer, Users


class RegisterForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        dev = Developer.query.filter_by(email=email.data).first()
        user = Users.query.filter_by(email=email.data).first()
        if user or dev:
            raise ValidationError('Email already exist in our system, please try another one')


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
