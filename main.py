from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, flash, request, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
import json
import os
import re
import hashlib
import secrets
import mailtrap as mt
import random
# from routes import *  # figure out how to split into pieces

app = Flask(__name__)

# detect config file

config_file = "debug.json"
prod_file_name = "/home/algorithmguy/mysite/configdata/prod.json"
if os.path.exists(prod_file_name):
    config_file = prod_file_name

# detect prod

working_dir = os.getcwd()
is_prod = ("/home/algorithmguy" in working_dir)

# make sure debug vs prod aligns

assert ("prod.json" in config_file) == is_prod, f"prod.json should not be available on non prod, and should not be missing on prod. {is_prod} {working_dir} {config_file}"

with open(config_file, "r") as f:
    config = json.load(f)

for key, value in config.items():
    app.config[key] = value


db = SQLAlchemy(app)


def disp_msg(msg):
    return render_template('blank.html', message=msg)


def get_salt_for_user(user_raw):
    user_hash, my_salt, pass_hash = user_pass(user_raw, "")
    sql_query = f'SELECT COALESCE((SELECT salt FROM user_credentials WHERE sha256user = "{user_hash}" ), "{my_salt}") as salt'
    result = db.engine.execute(sql_query)
    rows = result.fetchall()
    assert len(rows) == 1
    return rows[0][0]

def return_user_id(user_raw, pass_raw):
    my_salt = get_salt_for_user(user_raw)
    # Note:
    user_hash, my_salt, pass_hash = user_pass(user_raw, pass_raw, my_salt)
    sql_query = f'SELECT id FROM user_credentials WHERE sha256user = "{user_hash}" and sha256password="{pass_hash}"'
    result = db.engine.execute(sql_query)
    rows = result.fetchall()
    assert len(rows) < 2
    if len(rows):
        return int(rows[0][0])
    else:
        return None


def user_pass(user_raw, pass_raw, force_salt = None):
    user_raw = user_raw.strip().lower()
    pass_raw = pass_raw.strip()
    user_hash = hashlib.sha256(bytes(app.config['USER_PEPPER'] + user_raw, 'utf-8')).hexdigest()
    if force_salt is None:
        my_salt = secrets.token_hex(nbytes=32)
    else:
        my_salt = force_salt
    pass_hash = hashlib.sha256(bytes(app.config['PASS_PEPPER'] + my_salt + pass_raw, 'utf-8')).hexdigest()
    return user_hash, my_salt, pass_hash


class UserCredential(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now())
    sha256user = db.Column(db.String(64), nullable=False, unique=True)
    salt = db.Column(db.String(64), nullable=False)
    sha256password = db.Column(db.String(64), nullable=False)

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
        if too_many_registrations():
            good = False
            my_messages += "Too Many Registrations. Please wait longer\n"
        else:
            try:
                user_hash, salt, pass_hash = user_pass(email, password)
                new_user = UserCredential(sha256user=user_hash, salt=salt, sha256password=pass_hash)
                db.session.add(new_user)
                db.session.commit()
            except:
                good = False
                my_messages += "Failed to write record. Email already registered?\n"

    if good:
        return disp_msg("User created.")
    else:
        return render_template('register.html', form=form, messages=my_messages)


def is_logged_in():
    user = session.get('user')
    if user:
        return True


@app.route('/home')
def main_page():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    else:



        user = session.get('user')

        sql_query = f"""
              SELECT
              lessons.id,
              lessons.lesson_number,
              lessons.lesson_name,
              COALESCE(student_progress.lesson_finished, FALSE) AS lesson_finished
            FROM
              lessons
            LEFT JOIN
              student_progress ON lessons.id = student_progress.lesson_id
              AND student_progress.student_id = {int(user)}
            ORDER BY lessons.lesson_number;
        """
        result = db.engine.execute(sql_query)
        rows = result.fetchall()
        data = ""
        for r in rows:
            lesson_number = r[1]
            lesson_name = r[2]
            done = r[3]
            cd = "<li>$#!</li>"
            if done:
                data+=cd.replace("$#!", f'<a href="/lesson/{lesson_number}">{lesson_name}</a><span class="status completed">Done</span>')
            else:
                data+=cd.replace("$#!", f'<a href="/lesson/{lesson_number}">{lesson_name}</a><span class="status to-do">To Do</span>')

        lessons = f'\n<ul class="lesson-list">\n{data}\n</ul>'

        return render_template('home.html', lessons = lessons)


def is_violating_rate_limit(resource_string: str, resource_type: int, trigger_rate_cap:int, window_in_seconds:int, dont_write_just_check=False) -> bool:
    assert trigger_rate_cap > 0 and window_in_seconds > 0 and len(resource_string) == 64 and resource_type > 0 and resource_type < 256
    assert re.match("^[0-9a-fA-F]+$", resource_string)

    sql_query = f"""SELECT COUNT(id)
            FROM access_granted
            WHERE resource_type = {resource_type} AND resource_string = "{resource_string}" AND timestamp >= NOW() - INTERVAL {window_in_seconds} SECOND
        """
    result = db.engine.execute(sql_query)
    rows = result.fetchall()
    assert len(rows) == 1
    return_value = int(rows[0][0])

    if return_value >= trigger_rate_cap:
        return True

    if not dont_write_just_check:
        sql_query = f'INSERT INTO access_granted (resource_string, resource_type, timestamp) VALUES ("{resource_string}", {resource_type} , NOW())'
        result = db.engine.execute(sql_query)
    return False

def current_user_ip(additional_qualifier=""):
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    hashed_ip = hashlib.sha256(bytes(app.config['IP_PEPPER'] + additional_qualifier + ip_address, 'utf-8')).hexdigest()
    return hashed_ip

def successful_login_wipe_login_attempts(user_raw):
    user_hash, my_salt, pass_hash = user_pass(user_raw, "", "")
    myip = current_user_ip(user_hash)
    sql_query = f"""DELETE
            FROM access_granted
            WHERE resource_type = 1 AND resource_string = "{myip}"
        """
    db.engine.execute(sql_query)

def too_many_logins(user_raw):
    user_hash, my_salt, pass_hash = user_pass(user_raw, "", "")
    myip = current_user_ip(user_hash)
    if is_violating_rate_limit(myip, 1, 11, 600, dont_write_just_check=True):
        return True
    return is_violating_rate_limit(myip, 1, 3, 20)

def too_many_registrations():
    myip = current_user_ip()
    if is_violating_rate_limit(myip, 2, 101, 600, dont_write_just_check=True):
        return True
    return is_violating_rate_limit(myip, 2, 3, 1)

def too_many_password_reset_requests(user_raw):
    if too_many_registrations():
        return True

    user_hash, my_salt, pass_hash = user_pass(user_raw, "", "")
    myip = current_user_ip(user_hash)
    if is_violating_rate_limit(myip, 5, 2, 86400, dont_write_just_check=True):
        return True
    return is_violating_rate_limit(myip, 5, 1, 900)


def too_many_lessons(user_num):
    myip = current_user_ip(str(user_num))
    return is_violating_rate_limit(myip, 25, 7, 30)


@app.route('/blank')
def blank_page():
    return disp_msg("This is a blank page.")


@app.route('/', methods=['GET', 'POST'])
def login_page():
    messages = ""
    if is_logged_in():
        return redirect(url_for('main_page'))
    else:
        if request.method == 'POST':

            if too_many_logins(request.form['email']):
                messages += "Too many login attempts\n"
            else:
                email = request.form['email']
                password = request.form['password']
                my_id = return_user_id(email, password)
                if my_id is not None:
                    session['user'] = my_id
                    successful_login_wipe_login_attempts(email)
                    return redirect(url_for('main_page'))
                else:
                    messages += "User / combo not found."

    return render_template('login.html', messages = messages)


@app.route('/lesson/<int:num>')
def lesson_number(num):
    if num < 1 or num > 10000:
        return disp_msg("Invalid lesson number.")
    if not is_logged_in():
        return redirect(url_for('login_page'))
    user = session.get('user')
    if too_many_lessons(str(user)):
        return disp_msg("Too many requests, wait and retry.")
    session['lessonnumber'] = num

    return render_template('lessonformat.html', lessonnum=str(num))


@app.route('/completed/<int:num>')
def completed(num):
    if num < 1 or num > 10000:
        return disp_msg("Invalid lesson number.")
    if not is_logged_in():
        return redirect(url_for('login_page'))

    user = session.get('user')

    result = db.engine.execute(f"SELECT id FROM student_progress WHERE lesson_id = {num} AND student_id = {user}")

    rows = result.fetchall()
    if len(rows):
        db.engine.execute(f"UPDATE student_progress SET lesson_finished = 1 WHERE lesson_id = {num} AND student_id = {user}")
    else:
        db.engine.execute(f"INSERT INTO student_progress (lesson_id, student_id, lesson_finished) VALUES ({num}, {user}, 1)")

    return redirect(url_for('main_page'))


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   return redirect(url_for('login_page'))

def generate_reset_code():
    return ''.join(random.choice("ABCDEF234567Y9TX") for _ in range(13))

def send_email(email_address, reset_code):

    my_api_key = None
    with open('/home/algorithmguy/mysite/configdata/apikey.txt', 'r') as f:
        my_api_key = f.read().strip()
    assert my_api_key is not None and len(my_api_key) > 0, "Failed to load api_key!"


    mail = mt.Mail(
        sender=mt.Address(email="noreply@eslquickreads.com", name="Test"),
        to=[mt.Address(email=email_address)],
        subject="Esl Quick ReadsPassword Reset Code",
        text=f"""\
Return to ESL Quick Reads and use the following code to reset your password:

{reset_code}

If you did not request a password reset, you can ignore this email.

Thank you.
""",
    )
    client = mt.MailtrapClient(token=my_api_key)
    client.send(mail)

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
        if too_many_password_reset_requests(form.email.data):
            good = False
            my_messages += "Too Many attempts.\n"
        else:
            user_hash, salt, pass_hash = user_pass(email, "")

            sql_query = f'SELECT id FROM user_credentials WHERE sha256user = "{user_hash}"'
            result = db.engine.execute(sql_query)
            rows = result.fetchall()
            assert len(rows) < 2
            if len(rows) == 0:
                good = False
            else:
                reset_code = generate_reset_code()
                sql_query = f"INSERT INTO password_resets (userhash, resetcode) VALUES ('{user_hash}', '{reset_code}');"
                result = db.engine.execute(sql_query)
                send_email(email, reset_code)


    if good:
        return disp_msg("""If your email exists in our records, a password reset email will be sent. Check your email for instructions to complete password reset.  If you can't find it, be sure to check your spam folder. Password reset code expires in 15 minutes.
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
            user_hash, salt, pass_hash = user_pass(email, password)
            sql_query = f"""
                        SELECT *
            FROM password_resets
            WHERE userhash = '{user_hash}'
              AND resetcode = '{reset_code}'
              AND timestamp >= (NOW() - INTERVAL 15 MINUTE)
            ORDER BY timestamp DESC
            LIMIT 1;
            """
            result = db.engine.execute(sql_query)
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
            db.engine.execute(sql_query)

            sql_query = f"""
            DELETE FROM password_resets
            WHERE userhash = '{user_hash}' OR timestamp < NOW() - INTERVAL 1 DAY;
            """
            db.engine.execute(sql_query)

        except:
            good = False
            my_messages += "Failed to write record. Unknown error\n"

    if good:
        return disp_msg("User updated.  Return to login page to login! <a href='/'>Login Page</a>")
    else:
        return render_template('havecode.html', form=form, messages=my_messages)
