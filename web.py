import json
from flask import Flask, render_template, request, redirect, abort, session
import os
from auth0 import auth0, auth0_setup, require_auth
from flask.helpers import flash, url_for
from urllib.parse import urlencode

import db;
import posts as postsAPI;

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

@app.before_first_request
def initialize():
  db.setup()
  auth0_setup()

# Authentication
@app.route('/callback')
def callback():
  auth0().authorize_access_token()
  resp = auth0().get('userinfo')
  userinfo = resp.json()

  session['jwt_payload'] = userinfo
  session['profile'] = {
    'user_id': userinfo['sub'],
    'user_name': userinfo['name'],
    'user_email': userinfo['email'],
    'user_avatar': userinfo['picture'],
    'user_nickname': userinfo['nickname']
  }

  return redirect('/')

# @app.route('/login')
# def login():
#   return auth0().authorize_redirect(redirect_uri=url_for('callback', _external=True))

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/signup')
def signup():
  return render_template('signup.html')

@app.route('/logout')
def logout():
  session.clear()
  params = { 'returnTo': url_for('index', _external=True), 'client_id': os.environ['AUTH0_CLIENT_ID']}
  return redirect(auth0().api_base_url + '/v2/logout?' + urlencode(params))

# Root
@app.route('/')
def index():
  posts = postsAPI.get_all_posts()
  return render_template('index.html', posts=posts)

@app.route('/posts')
def posts():
  posts = postsAPI.get_all_posts()
  return render_template('index.html', posts=posts)

@app.route('/posts/<int:post_id>')
def post(post_id):
  post = postsAPI.get_post(post_id)
  if post is None:
    abort('404')
  return render_template('single_post.html', post=post)

@app.route('/newpost', methods=["GET", "POST"])
def new_post():
  if request.method == "POST":
    title = request.form['title']
    content = request.form['content']

    if not title:
      flash('Title is required')
    else:
      postsAPI.create_post(title, content)
      return redirect(url_for('index'))
  return render_template('new_post.html')

@app.route('/post_edit?post_id=<post_id>', methods=["GET", "POST"])
def edit_post(post_id):
  post = postsAPI.get_post(post_id)
  if request.method == "POST":
    title = request.form['title']
    content = request.form['content']

    if not title:
      flash('Title is required')
    else:
      postsAPI.update_post(post_id, title, content)
      return redirect(url_for('index'))
  return render_template('edit_post.html', post=post)

@app.route('/post_delete?post_id=<post_id>', methods=["POST"])
def delete_post(post_id):
  postsAPI.delete_post(post_id)
  return redirect(url_for('index'))

@app.route('/profile')
def profile():
  return render_template('profile.html')

@app.errorhandler(404)
def error404(error):
  return render_template('404.html')

def csrf_token():
  return ""