#-*-coding:utf-8-*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'You Shall Not Pass'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	FLASKY_MAIL_SUBJECT_PREFIX = '[Flask]'
	FLASKY_MAIL_SENDER = 'JoJo <whr428@163.com>'
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or 'whr428@163.com'
	FLASKY_POSTS_PER_PAGE = 20
	FLASKY_FOLLOWERS_PER_PAGE = 20
	SQLALCHEMY_RECORD_QUERIES = True
	FLASKY_DB_QUERY_TIMEOUT = 0.5
	FLASKY_SLOW_DB_QUERY_TIME=0.5
	SSL_DISABLE = True
	
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.163.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'whr428@163.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'whr072547227'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')
		
class TestingConfig(Config):
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///'+os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///'+os.path.join(basedir,'data.sqlite')
	
	@classmethod
	def init_app(cls,app):
		Config.init_app(app)
		
		#发送错误到管理员邮箱
		import logging
		from logging.handlers import SMTPHandler
		credentials = None
		secure = None
		if getattr(cls,'MAIL_USERNAME',None) is not None:
			credentials = (cls.MAIL_USERNAME,cls.MAIL_PASSWORD)
			if getattr(cls,'MAIL_USE_TLS',None):
				secure = ()
		mail_handler = SMTPHandler(
			mailhost=(cls.MAIL_SERVER,cls.MAIL_PORT),
			fromaddr=cls.FLASKY_MAIL_SENDER,
			toaddrs=[cls.FLASKY_ADMIN],
			subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + 'Application Error',
			credentials=credentials,
			secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
	SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
	@classmethod
	def init_app(cls,app):
		ProductionConfig.init_app(app)
		
		#输出到stderr
		import logging
		from logging import StreamHandler
		file_handler = Streamhandler()
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)
		
		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)
		
		
config = {
	'development':DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionConfig,
	'default':DevelopmentConfig,
	'heroku':HerokuConfig
}