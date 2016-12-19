from datetime import datetime
from flask import Flask,render_template,session,redirect,url_for,current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import User
from .. email import send_mail

@main.route('/user',methods=['GET','POST'])
def user():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.name.data).first()
		if user == None:
			user = User (username = form.name.data)
			db.session.add(user)#session in db
			session['known']=False#session in template
			if current_app.config['FLASKY_ADMIN']:
				send_mail(current_app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data=''
		return redirect(url_for('.user'))
	return render_template('user.html',form=form,name=session.get('name'),known=session.get('known',False))
	
@main.route('/')
def index():
    return render_template('index.html',
							current_time=datetime.utcnow())