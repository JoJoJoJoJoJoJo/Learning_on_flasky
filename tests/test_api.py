#-*-coding:utf-8-*-

import unittest,json,re
from app import create_app,db
from app.models import User,Post,Role,Comment
from flask import url_for
from base64 import b64encode


class FlaskAPITestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client()
		
	def teardown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()
	
	def get_api_headers(self,username,password):
		return {
			'Authorization':'Basic '+b64encode((username+':'+password).encode('utf-8')).decode('utf-8'),
			'Accept':'application/json',
			'Content-Type':'application/json'}
			
	def test_no_auth(self):
		response = self.client.get(url_for('api.get_posts'),content_type='application/json')
		self.assertTrue(response.status_code == 200)
		
	def test_posts(self):
		#添加用户
		r = Role.query.filter_by(name='USER').first()
		self.assertIsNotNone(r)
		u = User(email='whr428@qq.com',password='okayyy',confirmed=True,role=r)
		db.session.add(u)
		db.session.commit()
		
		#添加新文章
		response = self.client.post(
			url_for('api.new_post'),
			headers=self.get_api_headers('whr428@qq.com','okayyy'),
			data = json.dumps({'body':'ohyaaaaaaaaaaa'}))
		self.assertTrue(response.status_code == 201)
		url = response.headers.get('Location')
		self.assertIsNotNone(url)
		
		#获取刚发布的文章
		response = self.client.get(url,headers=self.get_api_headers('whr428@qq.com','okayyy'))
		self.assertTrue(response.status_code == 200)
		json_response = json.loads(response.data.decode('utf-8'))
		self.assertTrue(json_response['url']==url)
		self.assertTrue(json_response['body']=='ohyaaaaaaaaaaa')
		self.assertTrue(json_response['body_html'] == '<p>ohyaaaaaaaaaaa</p>')