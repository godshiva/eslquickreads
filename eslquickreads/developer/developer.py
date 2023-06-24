import os
import secrets
from eslquickreads import app, db
from flask import render_template, url_for, flash, redirect, request, session, jsonify
from flask_login import login_user, current_user, login_required
from datetime import datetime
from eslquickreads.developer.forms.developer_forms import AddLessonForm
from eslquickreads.lesson.models.model_lesson import Lesson, LessonsPrompt
from eslquickreads.route.models.user_models import Users, Developer


def save_audio_pdf(from_pdf):
    """Save audio file"""
    random_hex = secrets.token_hex(8)  # random token name for pdf 8 char long
    _, f_ext = os.path.splitext(from_pdf.filename)  # splitting original file in name and extension
    pdf_fn = random_hex + f_ext  # creating new name with original extension
    isFile = os.path.isdir(f'{app.root_path}/static/audios')
    if isFile:
        pass
    else:
        # Path
        path = os.path.join(app.root_path, 'static/', 'audios')
        os.mkdir(path)
    pdf_path = os.path.join(app.root_path, 'static/audios', pdf_fn)  # save to specific path
    from_pdf.save(pdf_path)
    return pdf_fn  # return file name


@app.route("/add-lessons", methods=['GET', 'POST'])
@login_required
def add_lesson():
    if current_user not in Developer.query.all():
        flash('Unauthorized User', 'warning')
        return redirect(url_for('home'))
    form = AddLessonForm()
    if form.validate_on_submit():
        session['lesson_name'] = form.lesson_name.data
        session['description'] = form.description.data
        if form.audio_file.data:
            file_audio = save_audio_pdf(form.audio_file.data)
            if session.get('all_prompts'):
                session['all_prompts'].append([file_audio, form.file_text.data])
            else:
                session['all_prompts'] = []
                session['all_prompts'].append([file_audio, form.file_text.data])
        flash('Prompt added successfully', 'success')
        return redirect(url_for('add_lesson'))
    elif request.method == "GET":
        form.lesson_name.data = session.get('lesson_name')
        form.description.data = session.get('description')
    return render_template('developer/developer.html', title='Add Lessons', Developer=Developer, form=form)


@app.route("/all_developers", methods=['GET', 'POST'])
@login_required
def all_developers():
    if current_user not in Developer.query.all():
        flash('Unauthorized User', 'danger')
        return redirect(url_for('home'))
    return render_template('developer/all_developer.html', title='All Developers', Developer=Developer)


@app.route("/all_users", methods=['GET', 'POST'])
@login_required
def all_users():
    if current_user not in Developer.query.all():
        flash('Unauthorized User', 'danger')
        return redirect(url_for('home'))
    users = Users.query.all()
    return render_template('developer/all_users.html', title='All Users', Developer=Developer, users=users)


@app.route("/remove_prompt/<string:audio_file>", methods=['GET', 'POST'])
@login_required
def remove_prompt(audio_file):
    if current_user not in Developer.query.all():
        flash('Unauthorized User', 'danger')
        return redirect(url_for('home'))
    if session.get('all_prompts'):
        for all_prompt in session.get('all_prompts'):
            if all_prompt[0] == audio_file:
                session['all_prompts'].remove(all_prompt)
                session['all_prompts'] = session['all_prompts']
                flash('Prompt Removed', 'success')
                return redirect(url_for('add_lesson'))
    flash('Unauthorized request', 'warning')
    return redirect(url_for('add_lesson'))


@app.route("/add_lessons/developer", methods=['GET', 'POST'])
@login_required
def developer_prompt():
    if current_user not in Developer.query.all():
        flash('Unauthorized User', 'danger')
        return redirect(url_for('home'))
    if session.get('all_prompts'):
        lesson_hex = Lesson.query.all()
        token = secrets.token_hex(16)
        for pol in lesson_hex:
            if pol.hex == token:
                token = secrets.token_hex(16)

        lesson = Lesson(hex=token, lesson_name=session['lesson_name'],
                        description=session['description'],
                        date_created=datetime.now())
        db.session.add(lesson)
        db.session.commit()
        for all_prompt in session.get('all_prompts'):

            lesson_hex = LessonsPrompt.query.all()
            token = secrets.token_hex(16)
            for pol in lesson_hex:
                if pol.hex == token:
                    token = secrets.token_hex(16)

            lesson_prompt = LessonsPrompt(hex=token, file_name=all_prompt[0], audio_text=all_prompt[1],
                                          date_created=datetime.now(), lesson=lesson)
            db.session.add(lesson_prompt)

        db.session.commit()
        session.pop('lesson_name')
        session.pop('description')
        session.pop('all_prompts')
        flash('Lesson added successfully', 'success')
        return redirect(url_for('home'))
    flash('Unauthorized request', 'warning')
    return redirect(url_for('add_lesson'))
