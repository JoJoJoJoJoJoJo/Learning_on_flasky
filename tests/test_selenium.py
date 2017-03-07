#-*-coding:utf-8-*-

from selenium import webdriver
from app import db,create_app
from app.models import User,Role,Post,Permission
import threading
import re
import unittest

class SeleniumTestCase(unittest.TestCase):
	client = None
	
	@classmethod
	def setUpClass(cls):
		#启动Firefox
		try:
			cls.client = webdriver.Firefox()
		except:
			pass
			
		#如果无法启动浏览器则跳过这些测试
		if cls.client:
			#创建程序
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()
			
			#禁止日志，保证输出简洁
			import logging
			logger = logging.getLogger('werkzeug')
			logger.setLever('ERROR')
			
			#创建数据库，使用虚拟数据填充
			db.create_all()
			Role.insert_roles()
			User.generate_fake(10)
			Post.generate_fake(10)
			
			#添加管理员
			admin_role = Role.query.filter_by(permission=0xff).first()
			admin = User(
				email='abc@def.com',username='g',password='666666',role=admin_role,confirmed=True)
			db.session.add(admin)
			db.session.commit()
			
			#在一个线程中启动Flask服务器
			threading.Thread(target=cls.app.run).start()
			
	@classmethod
	def tearDownClass(cls):
		if cls.client:
			#关闭Flask服务器和浏览器
			cls.client.get('http://localhost:5000/shutdown')
			cls.client.close()
			
			#销毁数据库
			db.drop_all()
			db.session.remove()
			
			#删除程序上下文
			cls.app_context.pop()
			
	def setUp(self):
		if not self.client:
			self.skipTest('Web browser not avilable')
			
	def tearDown(self):
		pass
		
	def test_admin_home_page(self):
		#进入首页
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello World',self.client.page_source))
		
		#进入登录界面
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)
		
		#登录
		self.client.find_element_by_name('email').send_keys('abc@def.com')
		self.client.find_element_by_name('password').send_keys('666666')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Welcome,g',self.client.page_source))
		
		#进入用户个人资料页面
		self.client.find_element_by_link_text('Profile').click()
		self.assertTrue('<h1>g</h1>' in self.client.page_source)