from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import *

class NameForm(FlaskForm):
	name = StringField("What's your name?",validators=[Regexp(r'[A-Z][a-z]+$|[A-Z][a-z]+\s[A-Z][a-z]+')])
	submit = SubmitField('Submit')