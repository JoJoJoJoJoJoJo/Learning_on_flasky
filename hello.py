from flask import Flask,render_template,session,redirect,url_for,flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import *

class NameForm(FlaskForm):
	name = StringField("What's your name?",validators=[Regexp(r'[A-Z][a-z]+$|[A-Z][a-z]+\s[A-Z][a-z]+')])
	submit = SubmitField('Submit')
	
app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY']='You Shall Not Pass'

@app.route('/user',methods=['GET','POST'])
def user():
	form = NameForm()
	if form.validate_on_submit():
		old_name=session.get('name')
		if old_name is not None and old_name!=form.name.data:
			flash('Why you changed your name?')
		session['name'] = form.name.data
		return redirect(url_for('user'))
	return render_template('user.html',name=session.get('name'),form = form)

@app.route('/')
def index():
    return render_template('index.html',
							current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404
	
if __name__== '__main__':
    manager.run()
