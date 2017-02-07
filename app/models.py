from flask_sqlalchemy import SQLAlchemy
from . import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Role(db.Model):
	__tablename__ = 'roles'
	id=db.Column(db.Integer,primary_key = True)
	name = db.Column(db.String(64),unique = True)
	default = db.Column(db.Boolean,default = False,index = True)
	permissions = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Role %r>'% self.name
	
	users = db.relationship('User',backref = 'role',lazy = 'dynamic')
	
	@staticmethod
	def insert_roles():
		roles = {
			'USER':(Permission.FOLLOW |
					Permission.COMMENT |
					Permission.WRITE_ARTICLES,True),
			'Moderator':(Permission.FOLLOW |
						Permission.COMMENT |
						Permission.WRITE_ARTICLES |
						Permission.MODERATE_COMMENTS,False),
			'Adminstrator':(0xff,False)
		}
		for r in roles:
			role = Role.query.filter_by(name = r).first()
			if role is None:
				role = Role(name = r )
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()
		
class User(UserMixin,db.Model):
	__tablename__ = 'users'
	password_hash = db.Column(db.String(128))
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(64),unique = True,index = True)
	email = db.Column(db.String(64),unique = True,index = True)
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean,default = False)
	
	@property
	def password(self):
		raise AttributeError('password is not readable')
		
	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)
	
	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)
	
	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))
	
	def generate_confirmation_token(self,expirtion = 3600):
		s = Serializer(current_app.config['SECRET_KEY'],expirtion)
		return s.dumps({'confirm':self.id})
		
	def confirm(self,token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm')!=self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True
	
	def can(self,permissions):
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions
	def is_adminstrator(self):
		return self.can(Permission.ADMINSTER)
		
	def __init__(self,**args):
		super(User,self).__init__(**args)
		if self.role is None:
			if self.email == current_app.config['FLASKY_ADMIN']:
				self.role = Role.query.filter_by(permissions = 0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default = True).first()
				
	def __repr__(self):
		return '<User %r>' % self.username
	
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

	
class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINSTER = 0x80


class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False
	
	def is_adminstrator(self):
		return False
		
login_manager.anonymous_user = AnonymousUser