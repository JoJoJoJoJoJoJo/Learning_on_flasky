from flask import Flask,render_template,session,redirect,url_for,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import *
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail,Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))
class NameForm(FlaskForm):
	name = StringField("What's your name?",validators=[Regexp(r'[A-Z][a-z]+$|[A-Z][a-z]+\s[A-Z][a-z]+')])
	submit = SubmitField('Submit')
	
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=\
	'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] =True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db= SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY']='You Shall Not Pass'
migrate =Migrate(app,db)
manager.add_command('db',MigrateCommand)
app.config['MAIL_SERVER']='smtp.163.com'
app.config['MAIL_PORT']=25
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
app.config['FLASKY_MAIL_SUBJECT_PREFIX']='[Flasky]'
app.config['FLASKY_MAIL_SENDER']='Flasky Admin <whr428@163.com>'
app.config['FLASKY_ADMIN']=os.environ.get('FLASKY_ADMIN')

class Role(db.Model):
	__tablename__ = 'roles'
	id=db.Column(db.Integer,primary_key = True)
	name = db.Column(db.String(64),unique = True)
	
	def __repr__(self):
		return '<Role %r>'% self.name
	
	users = db.relationship('User',backref = 'role',lazy = 'dynamic')
	
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(64),unique = True,index = True)
	
	def __repr__ (self):
		return '<User %r>' % self.username
	
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role)
manager.add_command('shell',Shell(make_context=make_shell_context))

@app.route('/user',methods=['GET','POST'])
def user():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.name.data).first()
		if user == None:
			user = User (username = form.name.data)
			db.session.add(user)#session in db
			session['known']=False#session in template
			if app.config['FLASKY_ADMIN']:
				send_mail(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data=''
		return redirect(url_for('user'))
	return render_template('user.html',form=form,name=session.get('name'),known=session.get('known',False))

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)

def send_mail(to,subject,template,**args):
	msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
				sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	msg.body=render_template(template+'.txt',**args)
	msg.html=render_template(template+'.html',**args)
	thr = Thread(target = send_async_email,args = [app,msg])
	thr.start()
	return thr
	
@app.route('/')
def index():
    return render_template('index.html',
							current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404
	
if __name__== '__main__':
    manager.run()
