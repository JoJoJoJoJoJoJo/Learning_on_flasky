#-*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,SelectField,BooleanField,ValidationError
from wtforms.validators import *
from ..models import User,Role,Post
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField,FileAllowed,FileRequired
from .. import photos

class NameForm(FlaskForm):
	name = StringField("What's your name?",validators=[Regexp(r'[A-Z][a-z]+$|[A-Z][a-z]+\s[A-Z][a-z]+')])
	submit = SubmitField('Submit')
	
class EditProfileForm(FlaskForm):
	name = StringField('Real name',validators=[Length(0,64)])
	location = StringField('Location',validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	photo = FileField(u'上传头像',validators=[
		Optional(),
		FileAllowed(photos,u'图片格式不支持！')])
	submit = SubmitField('Submit')
	
class EditProfileAdminForm(FlaskForm):
	email = StringField('Email',validators=[Required(),Length(1,64),Email()])
	username = StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z0-9_.]*$',0,
		'Username must have only letters,'
		'numbers,dots or underscores')])
	confirmed = BooleanField('Confirmed')
	role = SelectField('Role',coerce=int)
	name = StringField('Real name',validators=[Length(0,64)])
	location = StringField('Location',validators=[Length(0,64)])
	about_me = TextAreaField('About Me')
	photo = FileField(u'上传头像',validators=[Optional(),FileAllowed(['jpg','png','bmp','jpeg'],u'头像必须是图片格式！')])
	submit = SubmitField('Submit')
	
	def __init__(self,user,*args,**kw):
		super(EditProfileAdminForm,self).__init__(*args,**kw)
		self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user
		
	def validate_email(self,field):
		if field.data != self.user.email and \
			User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already exists')
			
	def validate_username(self,field):
		if field.data != self.user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already exists')

class PostForm(FlaskForm):
	body = PageDownField('write something',validators = [Required()])
	submit = SubmitField('Submit')

class CommentForm(FlaskForm):
	body = StringField('',validators=[Required()])
	submit = SubmitField('Submit')
	
class UserQueryForm(FlaskForm):
	username = StringField(u'用户名',validators=[Length(0,64)])
	email = StringField(u'邮件地址',validators=[Optional(),Length(0,64),Email()])
	submit = SubmitField(u'查找用户')