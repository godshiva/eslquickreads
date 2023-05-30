from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from eslquickreads.lesson.models.model_lesson import Lesson
from flask_wtf.file import FileField, FileAllowed


class AddLessonForm(FlaskForm):
    lesson_name = StringField("lesson_name", validators=[DataRequired()])
    description = StringField("description", validators=[DataRequired()])
    audio_file = FileField('audio_file', validators=[FileAllowed(['mp3'])])
    file_text = StringField("file_text", validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_lesson_name(self, lesson_name):
        dev = Lesson.query.filter_by(lesson_name=lesson_name.data).first()
        if dev:
            raise ValidationError('Lesson name already exists in our system, please try another one')
