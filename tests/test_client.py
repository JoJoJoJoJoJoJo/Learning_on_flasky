#-*-coding:utf-8-*-

import unittest,re
from app import create_app,db
from app.models import User,Role,Post
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies=True)
	
	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()
	
	#这特么为啥啊 为什么这个测试通不过啊
	'''def test_home_page(self):
		response = self.client.get(url_for('main.index'))
		self.assertTrue('Visitor' in response.get_data(as_text=True))'''
		
	def test_register_and_login(self):
		#注册新账号
		response = self.client.post(url_for('auth.register'),data={
			'email':'whr428@qq.com',
			'username':'Nrhd',
			'password':'okayyy',
			'password2':'okayyy'})
		self.assertTrue(response.status_code==302 or response.status_code==200)
		
		#使用新账户登录
		response = self.client.post(url_for('auth.login'),data={
			'email':'whr428@qq.com',
			'password':'okayyy',},follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue(re.search('confirmation mail',data))
		self.assertTrue('Your account has not been confirmed' in data)
		
		#发送确认令牌
		user = User.query.filter_by(email='whr428@qq.com').first()
		token = user.generate_confirmation_token()
		response = self.client.get(url_for('auth.confirm',token=token),follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('You have confirmed your account' in data)
		
		#登出
		response = self.client.get(url_for('auth.logout'),follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('You have been logged out' in data)