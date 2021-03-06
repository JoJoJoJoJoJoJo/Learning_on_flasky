from flask_mail import Mail,Message
from threading import Thread
from flask import current_app,render_template,Flask
from . import mail




def send_mail(to,subject,template,**args):
	app = current_app._get_current_object()# Necessery
	msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
				sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	msg.body=render_template(template+'.txt',**args)
	msg.html=render_template(template+'.html',**args)
	thr = Thread(target = send_async_email,args = [app,msg])
	thr.start()
	return thr

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)	