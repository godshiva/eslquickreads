from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class SelectLanguageForm(FlaskForm):
    language = SelectField('language', choices=[('', 'Select language'), ('fr', 'french'), ('de', 'German'),
                                                ('es', 'Spanish')])
    submit = SubmitField('Submit')
