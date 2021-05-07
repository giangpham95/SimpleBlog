from flask import Flask, render_template, request, redirect, abort
import os

from flask.helpers import flash, url_for

import db;
import posts as postsAPI;

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

@app.before_first_request
def initialize():
  db.setup()

# Authentication
@app.route('/login')
def login():
  return "Hello"

@app.route('/logout')
def logout():
  return "Hi"

# Root
@app.route('/')
def index():
  posts = postsAPI.get_all_posts()
  return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
  post = postsAPI.get_post(post_id)
  if post is None:
    abort('404')
  return render_template('single_post.html', post=post)

@app.route('/newpost', methods=("GET", "POST"))
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

@app.route('/post_edit?post_id=<post_id>', methods=("GET", "POST"))
def edit_post(post_id):
  post = postsAPI.get_post(post_id)
  if request.method == "POST":
    title = request.form['title']
    content = request.form['content']

    if not title:
      flash('Title is required')
    else:
      postsAPI.create_post(title, content)
      return redirect(url_for('index'))
  return render_template('edit_post.html', post=post)

@app.errorhandler(404)
def error404(error):
  return render_template('404.html')

def csrf_token():
  return ""