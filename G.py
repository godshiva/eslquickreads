import os
import json
from flask_sqlalchemy import SQLAlchemy
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


class G:
    app = None
    db = None

    def __init__(self, my_app):
        G.app = my_app

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
            G.app.config[key] = value


        G.db = SQLAlchemy(G.app)

    @staticmethod
    def disp_msg(msg):
        return render_template('blank.html', message=msg)

    @staticmethod
    def is_logged_in():
        user = session.get('user')
        if user:
            return True

    @staticmethod
    def is_violating_rate_limit(resource_string: str, resource_type: int, trigger_rate_cap:int, window_in_seconds:int, dont_write_just_check=False) -> bool:
        assert trigger_rate_cap > 0 and window_in_seconds > 0 and len(resource_string) == 64 and resource_type > 0 and resource_type < 256
        assert re.match("^[0-9a-fA-F]+$", resource_string)

        sql_query = f"""SELECT COUNT(id)
                FROM access_granted
                WHERE resource_type = {resource_type} AND resource_string = "{resource_string}" AND timestamp >= NOW() - INTERVAL {window_in_seconds} SECOND
            """
        result = G.db.engine.execute(sql_query)
        rows = result.fetchall()
        assert len(rows) == 1
        return_value = int(rows[0][0])

        if return_value >= trigger_rate_cap:
            return True

        if not dont_write_just_check:
            sql_query = f'INSERT INTO access_granted (resource_string, resource_type, timestamp) VALUES ("{resource_string}", {resource_type} , NOW())'
            result = G.db.engine.execute(sql_query)
        return False

    @staticmethod
    def current_user_ip(additional_qualifier=""):
        ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        hashed_ip = hashlib.sha256(bytes(G.app.config['IP_PEPPER'] + additional_qualifier + ip_address, 'utf-8')).hexdigest()
        return hashed_ip

    @staticmethod
    def successful_login_wipe_login_attempts(user_raw):
        user_hash, my_salt, pass_hash = G.user_pass(user_raw, "", "")
        myip = G.current_user_ip(user_hash)
        sql_query = f"""DELETE
                FROM access_granted
                WHERE resource_type = 1 AND resource_string = "{myip}"
            """
        G.db.engine.execute(sql_query)

    @staticmethod
    def too_many_logins(user_raw):
        user_hash, my_salt, pass_hash = G.user_pass(user_raw, "", "")
        myip = G.current_user_ip(user_hash)
        if G.is_violating_rate_limit(myip, 1, 11, 600, dont_write_just_check=True):
            return True
        return G.is_violating_rate_limit(myip, 1, 3, 20)

    @staticmethod
    def too_many_registrations():
        myip = G.current_user_ip()
        if G.is_violating_rate_limit(myip, 2, 101, 600, dont_write_just_check=True):
            return True
        return G.is_violating_rate_limit(myip, 2, 3, 1)

    @staticmethod
    def too_many_password_reset_requests(user_raw):
        if G.too_many_registrations():
            return True

        user_hash, my_salt, pass_hash = G.user_pass(user_raw, "", "")
        myip = G.current_user_ip(user_hash)
        if G.is_violating_rate_limit(myip, 5, 2, 86400, dont_write_just_check=True):
            return True
        return G.is_violating_rate_limit(myip, 5, 1, 900)

    @staticmethod
    def too_many_lessons(user_num):
        myip = G.current_user_ip(str(user_num))
        return G.is_violating_rate_limit(myip, 25, 7, 30)

    @staticmethod
    def get_salt_for_user(user_raw):
        user_hash, my_salt, pass_hash = G.user_pass(user_raw, "")
        sql_query = f'SELECT COALESCE((SELECT salt FROM user_credentials WHERE sha256user = "{user_hash}" ), "{my_salt}") as salt'
        result = G.db.engine.execute(sql_query)
        rows = result.fetchall()
        assert len(rows) == 1
        return rows[0][0]

    @staticmethod
    def return_user_id(user_raw, pass_raw):
        my_salt = G.get_salt_for_user(user_raw)
        # Note:
        user_hash, my_salt, pass_hash = G.user_pass(user_raw, pass_raw, my_salt)
        sql_query = f'SELECT id FROM user_credentials WHERE sha256user = "{user_hash}" and sha256password="{pass_hash}"'
        result = G.db.engine.execute(sql_query)
        rows = result.fetchall()
        assert len(rows) < 2
        if len(rows):
            return int(rows[0][0])
        else:
            return None

    @staticmethod
    def user_pass(user_raw, pass_raw, force_salt = None):
        user_raw = user_raw.strip().lower()
        pass_raw = pass_raw.strip()
        user_hash = hashlib.sha256(bytes(G.app.config['USER_PEPPER'] + user_raw, 'utf-8')).hexdigest()
        if force_salt is None:
            my_salt = secrets.token_hex(nbytes=32)
        else:
            my_salt = force_salt
        pass_hash = hashlib.sha256(bytes(G.app.config['PASS_PEPPER'] + my_salt + pass_raw, 'utf-8')).hexdigest()
        return user_hash, my_salt, pass_hash

    @staticmethod
    def generate_reset_code():
        return ''.join(random.choice("ABCDEF234567Y9TX") for _ in range(13))

    @staticmethod
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