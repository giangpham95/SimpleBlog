from blog import get_all_draft_entries, get_all_entries, get_all_published_entries, get_blog_entry_by_slug, new_blog_entry
from auth import login_required, login_user, register_user
import json
from flask import Flask, render_template, request, redirect, abort, session
import os
from flask.helpers import flash, url_for
from urllib.parse import urlencode
import datetime

import db

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

@app.before_first_request
def initialize():
  db.setup()

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == "POST":
    login_username = request.form.get('login_username', None)
    login_password = request.form.get('login_password', None)
    if login_password is None:
      flash('Password is required.', 'danger')
    if login_username is None:
      flash('Username or Email Address is require.', 'danger')
    response = login_user(login_username, login_password)
    if response['error']:
      flash(response['error'], 'danger')
    else:
      session['user'] = response['data']
      flash('You were successfully logged in', 'success')
      return redirect(url_for('index'))
  if session.get('user'):
    flash('Already logged in', 'info')
    return redirect(url_for('index'))
  return render_template('auth/login.html', meta_title="LogIn")

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    nickname = request.form.get('name', None)
    username = request.form.get('username', None)
    email = request.form.get('email', None)
    new_pass = request.form.get('new_pass', None)
    new_pass_again = request.form.get('new_pass_again', None)
    if nickname is None:
      flash('Please provide a name...', 'warning')
    if username is None:
      flash('Username is required', 'warning')
    if email is None:
      flash('Email is required')
    if new_pass is None or new_pass_again is None:
      flash("Password and password second time is required", 'warning')
    response = register_user(nickname, username, email, new_pass, new_pass_again)
    if response['error']:
      flash(response['error'], 'danger')
    else:
      flash('Successfuly register with provided information! You can now log in with username and password.', 'success')
      return redirect(url_for('login'))
  if session.get('user'):
    flash('Already logged in', 'info')
    flash('Please log out from current account before signup...', 'info')
    return redirect(url_for('index'))
  return render_template('auth/register.html', meta_title="Register")

@app.route('/logout/')
def logout():
  session.pop('user')
  return redirect(url_for('index'))

@app.route('/')
@app.route('/index/')
def index():
  response = get_all_published_entries()
  return render_template('index.html', entries=response['data'])

@app.route('/new_entry/', methods=['GET', 'POST'])
@login_required
def new_entry():
  current_user = session.get('user')
  if request.method == "POST":
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    published = 'published' in request.form
    if not (title and content):
      flash("Title and Content are required", 'danger')
    else:
      response = new_blog_entry(title, content, current_user.get('id'), published=published)
      if response['error']:
        flash(response['error'], 'danger')
      else:
        flash('Successful Save Entry.', 'success')
        if published:
          return redirect(url_for('entry_detail', slug=response['data'].get('slug')))
        else:
          return redirect(url_for('edit_entry', slug=response['data'].get('slug')))
  return render_template('blogs/new_entry.html', meta_title="New Entry")

@app.route('/<slug>/edit_entry/', methods=['GET', 'POST'])
@login_required
def edit_entry(slug):
  response = get_blog_entry_by_slug(slug)
  if response['error']:
    abort(404)
  return render_template('blogs/edit_entry.html', meta_title="Edit Entry", entry=response['data'])

@app.route('/<slug>/', methods=['GET', 'POST'])
def entry_detail(slug):
  response = get_blog_entry_by_slug(slug)
  return render_template('blogs/entry_detail.html', meta_title="Entry Detail", entry=response['data'])

@app.route('/drafts/')
@login_required
def draft_entries():
  current_user = session.get('user')
  response = get_all_draft_entries(current_user.get('id'))
  return render_template('blogs/list_entries.html', meta_title='Draft Blog Entries', entries=response['data'])

@app.route('/published/')
@login_required
def published_entries():
  response = get_all_published_entries()
  return render_template('blogs/list_entries.html', meta_title='Published Blog Entries', entries=response['data'])

@app.route('/entries/')
@login_required
def all_entries():
  current_user = session.get('user')
  response = get_all_entries(current_user.get('id'))
  return render_template('blogs/list_entries.html', meta_title="All Blog Entries", entries=response['data'], content_title="Your Blog Entries")

@app.errorhandler(404)
def not_found(error):
  return render_template('404.html')

@app.errorhandler(403)
def not_authorized(error):
  return render_template('403.html')

@app.errorhandler(500)
def internal_server_error(error):
  return render_template('500.html')