from eslquickreads import db
from flask_login import UserMixin


class Lesson(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    hex = db.Column(db.String(120), nullable=True, unique=True)
    lesson_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False)
    lesson_prompt = db.relationship('LessonsPrompt', backref='lesson', lazy=True)
    lesson_history = db.relationship('LessonsHistory', backref='lesson', lazy=True)


class LessonsPrompt(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    hex = db.Column(db.String(120), nullable=True, unique=True)
    file_name = db.Column(db.String(120), nullable=True)
    audio_text = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete="CASCADE"), nullable=False)


class LessonsHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
