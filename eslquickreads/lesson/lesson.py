from eslquickreads import app, db
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user
from googletrans import Translator
from eslquickreads.lesson.form.lesson_form import SelectLanguageForm
from eslquickreads.lesson.models.model_lesson import Lesson, LessonsPrompt, LessonsHistory
from eslquickreads.route.models.user_models import Developer
from datetime import datetime


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    lessons = Lesson.query.filter_by(active=1).all()
    return render_template('lesson/home.html', title='Home', Developer=Developer, lessons=lessons,
                           LessonsPrompt=LessonsPrompt, LessonsHistory=LessonsHistory)


@app.route("/view/lesson/<string:lesson_hex>/<string:prompt_hex>", methods=['GET', 'POST'])
@login_required
def view_lesson(lesson_hex, prompt_hex):
    lessons = Lesson.query.filter_by(hex=lesson_hex).first()
    lessons_prompt = LessonsPrompt.query.filter_by(hex=prompt_hex, lesson=lessons).first()
    lessons_prompts = LessonsPrompt.query.filter_by(lesson=lessons).all()
    if not (lessons_prompt and lessons):
        flash('Unauthorized User', 'danger')
        return redirect(url_for('home'))
    next_no = 0
    next_prompt = 0
    for lessons_prompt1 in lessons_prompts:
        if lessons_prompt1.hex == prompt_hex:
            print(next_no, len(lessons_prompts), 'ppppppppppp')

            if (next_no + 1) >= len(lessons_prompts):
                next_prompt = 0
            else:
                next_prompt = lessons_prompts[next_no + 1]
        else:
            next_no += 1
    form = SelectLanguageForm()
    if form.validate_on_submit():
        translator = Translator()
        result = translator.translate(lessons_prompt.audio_text, src='en', dest=form.language.data)
        session['trans_text'] = result.text
        return redirect(url_for('view_lesson', lesson_hex=lesson_hex, prompt_hex=prompt_hex))
    return render_template('lesson/view_lesson.html', title='Home', Developer=Developer, lessons=lessons,
                           lessons_prompt=lessons_prompt, form=form, next_prompt=next_prompt)


@app.route("/complete/lesson/<string:lesson_hex>", methods=['GET', 'POST'])
@login_required
def complete_lesson(lesson_hex):
    lesson = Lesson.query.filter_by(hex=lesson_hex).first()
    if not lesson:
        flash('Unauthorized User', 'danger')
        return redirect(url_for('home'))
    history = LessonsHistory(lesson=lesson, user=current_user, date_created=datetime.now())
    db.session.add(history)
    db.session.commit()
    flash('Lesson completed successfully', 'success')
    return redirect(url_for('home'))


@app.route("/Translanguage", methods=['POST', 'GET'])
@login_required
def Translanguagea():
    language = request.form.get('language')
    text = request.form.get('text')
    if text and language:
        translator = Translator()
        result = translator.translate(text, src='en', dest=language)
        return jsonify({'valid': 'True', 'text': result.text})

    return jsonify({'error': 'missing data'})


@app.route("/Lesson-History", methods=['GET', 'POST'])
@login_required
def Lesson_History():
    lessons = LessonsHistory.query.filter_by(user=current_user).all()
    return render_template('lesson/history.html', title='Lesson History', Developer=Developer, lessons=lessons)
