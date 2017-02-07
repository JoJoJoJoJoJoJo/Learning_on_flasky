from functools import wraps
from flask import abort
from flask_login import current_app


def permission_required(permission):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args,**kw):
			if not current_user.can(permission):
				abort(403)
			return f(*args,**kw)
		return decorated_function
	return decorator
		
	def admin_required(f):
		return permission_required(Permission.ADMINSTER)(f)