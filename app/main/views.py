#-*-coding:utf-8-*-
from datetime import datetime
from flask import Flask,render_template,session,redirect,url_for,current_app,flash,request,make_response
from flask_login import login_required,current_user
from . import main
from .forms import *
from .. import db,photos
from ..models import User,Permission,Role,Post,Comment
from .. email import send_mail
from ..decorators import permission_required,admin_required
from flask_sqlalchemy import get_debug_queries
import os


@main.route('/users',methods=['GET','POST'])
def users():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.name.data).first()
		if user == None:
			user = User(username = form.name.data)
			db.session.add(user)#session in db
			session['known']=False#session in template
			if current_app.config['FLASKY_ADMIN']:
				send_mail(current_app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data=''
		return redirect(url_for('.users'))
	return render_template('users.html',form=form,name=session.get('name'),known=session.get('known',False))
	

@main.route('/',methods = ['GET','POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(body = form.body.data,author = current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('.index'))
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed',''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	page = request.args.get('page',1,type=int)
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page,
		per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out =False)
	posts = pagination.items
	return render_template('index.html',
		form = form,
		posts=posts,
		pagination=pagination,
		show_followed = show_followed)
							
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		if form.photo.has_file():
			try:
				os.remove((current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+current_user.avatar_hash+'.jpg'))
				os.remove((current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+current_user.avatar_hash+'.png'))
				os.remove((current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+current_user.avatar_hash+'.bmp'))
			except WindowsError:
				pass
			#有点麻烦，其实应该把所有文件统一保存成同一格式
			#在模板中定义文件大小
			filename = photos.save(form.photo.data,name=(current_user.avatar_hash+'.'))
			current_user.photo_url = photos.url(filename)
		db.session.add(current_user)
		flash('Your Profile has been updated')
		return redirect(url_for('.user',username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html',form=form)
	
@main.route('/edit-porfile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.mail=form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location=form.location.data
		user.about_me = form.about_me.data
		if form.photo.has_file():
			try:
				os.remove(current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+user.avatar_hash+'.jpg')
				os.remove(current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+user.avatar_hash+'.png')
				os.remove(current_app.config['UPLOADED_PHOTOS_DEST']+'\\'+user.avatar_hash+'.bmp')
			except WindowsError:
				pass
			filename = photos.save(form.photo.data,name=(user.avatar_hash+'.'))
			user.photo_url = photos.url(filename)
		db.session.add(user)
		flash('The profile has been updated')
		return redirect(url_for('.user',username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html',form=form,user=user)
	
@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		abort(404)
	posts = user.posts.order_by(Post.timestamp.desc()).all()
	return render_template('user.html',user=user,posts=posts)

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
	post= Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
			post=post,
			author=current_user._get_current_object())
		db.session.add(comment)
		flash(u'评论成功')
		return redirect(url_for('.post',id=post.id,page=-1))
	page = request.args.get('page',1,type=int)
	if page == -1:
		page = (post.comments.count() - 1)/20 +1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page,per_page=20,error_out=False)
	comments = pagination.items
	return render_template('post.html',posts = [post],form=form,comments=comments,pagination=pagination)
	
@main.route('/edit/<int:id>',methods = ['GET','POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author.id and not current_user.can(Permission.ADMINSTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('The post has been updated')
		return redirect(url_for('.post',id=post.id))
	form.body.data = post.body
	return render_template('edit_post.html',form=form)
	
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash(u'已关注，不可重复关注')
		return redirect(url_for('.user',username=username))
	current_user.follow(user)
	flash(u'关注%s成功'%username)
	return redirect(url_for('.user',username=username))

@main.route('/unfollow/<username>')
@login_required
def unfollow(uesrname):
	user= user.query.filter_by(username=username).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	if user.is_followed_by(current_user) is None:
		flash(u'尚未关注用户')
		return redirect(url_for('.user',username=username))
	current_user.unfollow(user)
	flash(u'已取消关注%s'%username)
	return redirect(url_for('.user',username=username))

@main.route('/followers/<username>')
def followers(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type=int)
	pagination = user.followers.paginate(page,
		per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out=False)
	follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',
		user=user,title=u'关注',
		endpoint='.followers',
		pagination=pagination,
		follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type=int)
	pagination = user.followed.paginate(page,per_page=20,error_out=False)
	followed = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',
		user=user,
		endpoint='.followed_by',
		title=u'关注他的',
		pagination=pagination,
		follows=followed)
							
@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed','',max_age=30*24*60*60)
	return resp
	
@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed','1',max_age=30*24*60*60)
	return resp
	
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page',1,type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page,per_page=20,error_out=False)
	comments = pagination.items
	return render_template('moderate.html',comments=comments,pagination=pagination,page=page)
	
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))
	
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))
	
@main.route('/shutdown')
def server_shutdown():
	if not current_app.testing:
		abort(404)
	shutdown = request.environ.get('werkzeug.server.shutdown')
	if not shutdown:
		abort(500)
	shutdown()
	return u'关机中'
	
@main.after_app_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
			current_app.logger.waring('Slow query: %s\nParamaters: %s\nDuration: %fs\nContext: %s\n' %(	
				query.statement,query.parameters,query.duration,query.context))
	return response
	
@main.route('/admin',methods=['GET','POST'])
@login_required
@permission_required(Permission.ADMINSTER)
def admin():
	form = UserQueryForm()
	user = User.query
	if form.validate_on_submit():
		if form.email.data and form.username.data:
			if user.filter_by(email=form.email.data).first().username != form.username.data:
				flash(u'用户名与邮箱不匹配，按照邮箱查询')
		elif form.username.data:
			q='%'+form.username.data+'%'
			user = User.query.filter(User.username.ilike(q)).order_by(User.role_id)
		else:
			user = User.query.order_by(User.role_id)
	page = request.args.get('page',1,type=int)
	pagination = user.paginate(page,per_page=20,error_out=False)
	users = [{
		'id':item.id,
		'username':item.username,
		'email':item.email,
		'confirmed':item.confirmed,
		'role':item.role,
		'member_since':item.member_since,
		'last_seen':item.last_seen
		} for item in pagination.items]
	return render_template('admin.html',form=form,users=users,pagination=pagination)