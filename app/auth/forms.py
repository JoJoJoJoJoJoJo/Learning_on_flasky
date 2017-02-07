from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,ValidationError
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from ..models import User

class LoginForm(FlaskForm):
	email = StringField('Email',validators = [Required(),Length(1,64),Email()])
	password = PasswordField('Password',validators = [Required(),Length(1,36)])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')
	
class RegistionForm(FlaskForm):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	username = StringField('Username',validators=[Required(),Length(1,64),Regexp(
		'^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only letters,numbers,dots or underscores')])
	password = PasswordField('Password',validators = [Required(),EqualTo(
		'password2',message = 'Passwords must match')])
	password2 = PasswordField('Comfirm Password',validators = [Required()])
	submit = SubmitField('Register')
	
	def validate_email(self,field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email already existed')
			
	def valdiate_username(self,field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError('Username already existed')
			
class ChangeForm(FlaskForm):
	ori_password = PasswordField(
	'Original Password',validators = [Required()])
	new_password = PasswordField('New Password',validators = [Required(),EqualTo('new_password2',message 	= 'Passwords must match')])
	new_password2 = PasswordField('Confirm New Password',validators = [Required()])
	submit = SubmitField('Submit')
	
class ForgetPasswordForm(FlaskForm):
	email = StringField('Your Email Address',validators = [Required(),EqualTo('email2',message 	= 'Emails must match')])
	email2 = StringField('Confirm Email Address',validators = [Required(),Length(1,64),Email()])
	submit = SubmitField('Send mail')
	
class ResetPasswordForm(FlaskForm):
	email = StringField('Email Address',validators = [Required(),Length(1,64),Email()])
	new_password = PasswordField('New Password',validators = [Required(),EqualTo('new_password2',message 	= 'Passwords must match')])
	new_password2 = PasswordField('Confirm New Password',validators = [Required()])
	submit = SubmitField('Submit')