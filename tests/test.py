import unittest
from flask import current_app
from app import create_app,db
from app.models import User,Role,Permission,AnonymousUser

class BasicsTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		
	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()
		
	def test_app_exists(self):
		self.assertFalse(current_app==None)
	
	def test_app_is_testing(self):
		self.assertTrue(current_app.config['TESTING'])

class UserModelTestCase(unittest.TestCase):
	def test_password_setter(self):
		u = User(password = '072547')
		self.assertTrue(u.password_hash is not None)
		
	def test_no_passowrd_getter(self):
		u = User(password = '072547')
		with self.assertRaises(AttributeError):
			u.password
			
	def test_password_verification(self):
		u = User(password = '072547')
		self.assertTrue(u.verify_password('072547'))
		self.assertFalse(u.verify_password('45454545a'))
		
	def test_password_salts_are_random(self):
		u1 = User(password = '072547')
		u2 = User(password = '072547')
		self.assertTrue(u1.password_hash != u2.password_hash)
	
	def test_roles_and_permissions(self):
		Role.insert_roles()
		u = User(email='aabc@eefe.com',password = '1244466666')
		self.assertTrue(u.can(Permission.WRITE_ARTICLES))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
		
	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))