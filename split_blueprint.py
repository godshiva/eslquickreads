from flask import Blueprint
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
from G import G


split_blueprint = Blueprint('split_blueprint', __name__)




@split_blueprint.route('/completed/<int:num>')
def completed(num):
    if num < 1 or num > 10000:
        return G.disp_msg("Invalid lesson number.")
    if not G.is_logged_in():
        return redirect(url_for('split_blueprint.login_page'))

    user = session.get('user')

    result = G.db.engine.execute(f"SELECT id FROM student_progress WHERE lesson_id = {num} AND student_id = {user}")

    rows = result.fetchall()
    if len(rows):
        G.db.engine.execute(f"UPDATE student_progress SET lesson_finished = 1 WHERE lesson_id = {num} AND student_id = {user}")
    else:
        G.db.engine.execute(f"INSERT INTO student_progress (lesson_id, student_id, lesson_finished) VALUES ({num}, {user}, 1)")

    return redirect(url_for('split_blueprint.main_page'))









@split_blueprint.route('/home')
def main_page():
    if not G.is_logged_in():
        return redirect(url_for('split_blueprint.login_page'))
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
        result = G.db.engine.execute(sql_query)
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








@split_blueprint.route('/lesson/<int:num>')
def lesson_number(num):
    if num < 1 or num > 10000:
        return G.disp_msg("Invalid lesson number.")
    if not G.is_logged_in():
        return redirect(url_for('split_blueprint.login_page'))
    user = session.get('user')
    if G.too_many_lessons(str(user)):
        return G.disp_msg("Too many requests, wait and retry.")
    session['lessonnumber'] = num

    return render_template('lessonformat.html', lessonnum=str(num))



@split_blueprint.route('/', methods=['GET', 'POST'])
def login_page():
    messages = ""
    if G.is_logged_in():
        return redirect(url_for('main_page'))
    else:
        if request.method == 'POST':

            if G.too_many_logins(request.form['email']):
                messages += "Too many login attempts\n"
            else:
                email = request.form['email']
                password = request.form['password']
                my_id = G.return_user_id(email, password)
                if my_id is not None:
                    session['user'] = my_id
                    G.successful_login_wipe_login_attempts(email)
                    return redirect(url_for('split_blueprint.main_page'))
                else:
                    messages += "User / combo not found."

    return render_template('login.html', messages = messages)





@split_blueprint.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user', None)
   return redirect(url_for('split_blueprint.login_page'))
