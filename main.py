from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, flash, request, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from split_blueprint import split_blueprint
import json
import os
import re
import hashlib
import secrets
import mailtrap as mt
import random
from G import G


app = Flask(__name__)
app.register_blueprint(split_blueprint)
G(app)

class UserCredential(G.db.Model):  # haven't quite figured out how to move this with the dependency like this
    __tablename__ = 'user_credentials'
    id = G.db.Column(G.db.Integer, primary_key=True, autoincrement=True)
    created_at = G.db.Column(G.db.TIMESTAMP, default=G.db.func.now())
    sha256user = G.db.Column(G.db.String(64), nullable=False, unique=True)
    salt = G.db.Column(G.db.String(64), nullable=False)
    sha256password = G.db.Column(G.db.String(64), nullable=False)


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Send Email')

class HaveCodeResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    verification_code = StringField('Secret Code', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')




@app.route('/forgotpassword/', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    good = False
    my_messages = ""
    email = form.email.data
    if email is not None:
        good = True

        if not form.validate_on_submit():
            good = False
            my_messages += "Form validation failed\n"

    if good:
        if G.too_many_password_reset_requests(form.email.data):
            good = False
            my_messages += "Too Many attempts.\n"
        else:
            user_hash, salt, pass_hash = G.user_pass(email, "")

            sql_query = f'SELECT id FROM user_credentials WHERE sha256user = "{user_hash}"'
            result = G.db.engine.execute(sql_query)
            rows = result.fetchall()
            assert len(rows) < 2
            if len(rows) == 0:
                pass
            else:
                reset_code = G.generate_reset_code()
                sql_query = f"INSERT INTO password_resets (userhash, resetcode) VALUES ('{user_hash}', '{reset_code}');"
                result = G.db.engine.execute(sql_query)
                G.send_email(email, reset_code)


    if good:
        return G.disp_msg("""If your email exists in our records, a password reset email will be sent. Check your email for instructions to complete password reset.  If you can't find it, be sure to check your spam folder. Password reset code expires in 15 minutes.
        Click <a href="/havecode/">here</a> to go to password reset form.

        """)
    else:
        return render_template('changepassword.html', form=form, messages=my_messages)


@app.route('/havecode/', methods=['GET', 'POST'])
def have_code():

    form = HaveCodeResetPasswordForm()
    good = False
    my_messages = ""
    if form.email.data is not None or form.password.data is not None and form.verification_code.data is not None:
        good = True

        if not form.validate_on_submit():
            good = False
            my_messages += "Form validation failed\n"

        if good:
            email = form.email.data
            password = form.password.data
            reset_code = form.verification_code.data

            if not re.match("^[A-Z0-9]+$", reset_code):
                good = False
                my_messages += "Invalid reset code format\n"

            confirm_password = form.confirm_password.data

            if password!=confirm_password:
                good = False
                my_messages += "Passwords do not match\n"

            if len(password) < 6:
                good = False
                my_messages += "Passwords length too low\n"

        if good:
            user_hash, salt, pass_hash = G.user_pass(email, password)
            sql_query = f"""
                        SELECT *
            FROM password_resets
            WHERE userhash = '{user_hash}'
              AND resetcode = '{reset_code}'
              AND timestamp >= (NOW() - INTERVAL 15 MINUTE)
            ORDER BY timestamp DESC
            LIMIT 1;
            """
            result = G.db.engine.execute(sql_query)
            rows = result.fetchall()
            assert len(rows) < 2
            if len(rows) == 0:
                good = False
                my_messages += "Did not find email password reset code\n"

    if good:
        try:
            sql_query = f"""
            UPDATE user_credentials
            SET salt = '{salt}', sha256password = '{pass_hash}'
            WHERE sha256user = '{user_hash}';
            """
            G.db.engine.execute(sql_query)

            sql_query = f"""
            DELETE FROM password_resets
            WHERE userhash = '{user_hash}' OR timestamp < NOW() - INTERVAL 1 DAY;
            """
            G.db.engine.execute(sql_query)

        except:
            good = False
            my_messages += "Failed to write record. Unknown error\n"

    if good:
        return G.disp_msg("User updated.  Return to login page to login! <a href='/'>Login Page</a>")
    else:
        return render_template('havecode.html', form=form, messages=my_messages)



@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    good = False
    my_messages = ""
    if form.email.data is not None or form.password.data is not None:
        good = True

        if not form.validate_on_submit():
            good = False
            my_messages += "Form validation failed\n"

        if good:
            email = form.email.data
            password = form.password.data
            if len(email) < 3 or '@' not in email or not re.match("^[a-zA-Z0-9_\\-\\.]+@.+$", email):
                good = False
                my_messages += "Invalid email format\n"

            for white in " \t\n\r":
                if white in email or white in password:
                    good = False
                    my_messages += "Whitespace not allowed in user or pass\n"

            confirm_password = form.confirm_password.data

            if password!=confirm_password:
                good = False
                my_messages += "Passwords do not match\n"

            if len(password) < 6:
                good = False
                my_messages += "Passwords length too low\n"

    if good:
        if G.too_many_registrations():
            good = False
            my_messages += "Too Many Registrations. Please wait longer\n"
        else:
            try:
                user_hash, salt, pass_hash = G.user_pass(email, password)
                new_user = UserCredential(sha256user=user_hash, salt=salt, sha256password=pass_hash)
                G.db.session.add(new_user)
                G.db.session.commit()
            except:
                good = False
                my_messages += "Failed to write record. Email already registered?\n"

    if good:
        return G.disp_msg("User created.")
    else:
        return render_template('register.html', form=form, messages=my_messages)












