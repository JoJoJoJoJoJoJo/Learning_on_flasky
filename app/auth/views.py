#-*-coding:GBK-*-
from flask import render_template,redirect,request,url_for,flash
from . import auth
from flask_login import login_required,login_user,logout_user,current_user
from ..models import User
from .forms import *
from .. import db
from ..email import send_mail

@auth.route('/login',methods = ['GET','POST'])
def login():#login
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for ('main.index'))
		flash('Invalid username or password')
	return render_template('auth/login.html',form=form)
	
@auth.route('/logout')
@login_required
def logout():#log out
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('main.index'))

@auth.route('/register',methods = ['GET','POST'])
def register():#register
	form = RegistionForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,
					username = form.username.data,
					password = form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_mail(user.email,'Confirm Regiseter','auth/email/confirm',user = user, token = token)
		flash('A confirmation email has been sent,confirm in 1h plz')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html',form=form)
	
@auth.route('/confirm/<token>')
@login_required
def confirm(token):#send confirm mail
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account.Welcome!')
	else:
		flash('Invalid link or expired')
	return redirect(url_for('main.index'))
	

@auth.before_app_request
def before_request():#unconfirmed login
	if current_user.is_authenticated \
			and not current_user.confirmed \
			and request.endpoint[:5] != 'auth.' \
			and request.endpoint != 'static':
		return redirect(url_for('auth.unconfirmed'))
	
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')
	
	
@auth.route('/confirm')
@login_required
def resend_confirmation():#resend mails
	token = current_user.generate_confirmation_token()
	send_mail(
		current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
	flash('A new confirmation mail has been sent to your mail')
	return redirect(url_for('main.index'))
	
@auth.route('/change',methods = ['GET','POST'])
@login_required
def change():
	form = ChangeForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.ori_password.data):
			current_user.password = form.new_password.data
			db.session.add(current_user)
			db.session.commit()
			flash('Password Changed Successfuly')
			return redirect(url_for('main.index'))
		else:
			flash('Wrong Password')
	return render_template('auth/change.html',form=form)

	
@auth.route('/reset/<token>')
def reset(token):
	user = User()
	if user.confirm(token):
		return redirect(url_for('auth.reset_password'))
	else:
		flash('invalid link')
	return redirect(url_for('main.index'))

@auth.route('/reset_password',methods = ['GET','POST'])
def reset_password():
	form = ResetPasswordForm()
	if form.validate_on_submit():
		if User.query.filter_by(email = form.email.data):
			user=db.session.query(User).filter_by(email=form.email.data).first()# 大坑，可以更改别人的密码
			user.password = form.new_password.data
			db.session.add(user)
			db.session.commit()
			flash('Password Reset successfuly')
			return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html',form = form)

	
@auth.route('/forget',methods = ['GET','POST'])
def forget():
	form = ForgetPasswordForm()
	if form.validate_on_submit():
		if User.query.filter_by(email = form.email.data):
			user = User()
			token = user.generate_confirmation_token()
			send_mail(
				form.email.data,'Reset Password','auth/email/reset',user = current_user,token = token)
			flash('A confirmation mail has been sent')
			return redirect(url_for('main.index'))
		else:
			flash('The mail has not been registered')
			return redirect(url_for('auth.register'))
	return render_template('auth/forget.html',form = form)