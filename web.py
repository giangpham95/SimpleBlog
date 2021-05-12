import blog
from auth import delete_user_profile, get_all_users, load_user, login_required, login_user, register_user, update_password, update_user_profile
from flask import Flask, render_template, request, redirect, abort, session
import os
from flask.helpers import flash, url_for
from urllib.parse import urlencode

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

@app.route('/profile/<username>/')
@login_required
def profile(username):
  current_user = session.get('user')
  if username == current_user.get('username'):
    profile = current_user
  else:
    role = current_user.get('role')
    if role != 'owner' or role != 'admin':
      abort(403)  
    profile = load_user(username)
  return render_template('users/profile.html', profile=profile, meta_title="Profile")

@app.route('/profile/<username>/update', methods=['GET', 'POST'])
@login_required
def update_profile(username):
  current_user = session.get('user')
  profile = None
  if username == current_user.get('username'):
    profile = current_user
  else:
    role = current_user.get('role')
    if role != 'owner' or role != 'admin':
      abort(403)  
    profile = load_user(username)
  if request.method == 'POST':
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    new_nickname = request.form.get('nickname')
    if new_username is None:
      flash("Username is required", 'warning')
    if new_email is None:
      flash("Email is required")
    if new_nickname is None:
      flash('Nickname is required')
    response = update_user_profile(username, new_nickname, new_username, new_email)
    if response['error']:
      flash(response['error'], 'danger')
    else:
      return redirect(url_for('profile', username=new_username))
  if profile is None:
    abort(404)
  
  return render_template('users/update_profile.html', username=username, profile=profile, meta_title="Update Profile")

@app.route('/profile/<username>/change-password/', methods=['GET','POST'])
@login_required
def change_password(username):
  if request.method == 'POST':
    if username != session.get('user').get('username') or session.get('user').get('role') != 'owner':
      abort(403)
    old_pass = request.form.get('old_pass', '')
    new_pass = request.form.get('new_pass', '')
    new_pass_again = request.form.get('new_pass_again', '')
    if not old_pass:
      flash('Old pass is require', 'danger')
    if not new_pass or not new_pass_again:
      flash('New pass is require', 'danger')
    response = update_password(username, old_pass, new_pass, new_pass_again)
    if response['error']:
      flash(response['error'], 'danger')
    else:
      flash('Successfully Update Password', 'success')
      return redirect(url_for('profile', username=username))
  return render_template('users/change_password.html', username=username, meta_title="Change Password")

@app.route('/profile/<username>/delete')
@login_required
def delete_profile(username):
  current_user =  session.get('user')
  if current_user.get('role') != 'admin' or current_user.get('role') != 'owner':
    abort(403)
  else:
    delete_user_profile(username)
    return redirect(url_for('list_users'))

@app.route('/profiles/')
@login_required
def list_users():
  #users = None
  response = get_all_users()
  return render_template('users/list_users.html', users=response['data'])

@app.route('/')
@app.route('/index/')
def index():
  response = blog.get_all_published_entries()
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
      response = blog.new_blog_entry(title, content, current_user.get('id'), published=published)
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
  lookup_response = blog.get_blog_entry_by_slug(slug)
  if lookup_response['error']:
    abort(404)
  entry = lookup_response['data']
  if request.method == "POST":
    title = request.form.get('title', None)
    content = request.form.get('content', None)
    published = 'published' in request.form
    if not (title and content):
      flash("Title and Content are required", 'danger')
    else:
      if entry['author_id'] != session.get('user').get('id'):
        flash('You have no right editing this entries')
        abort(403)
      response = blog.update_blog_entry(entry['id'], title, content, published)
      if response['error']:
        flash(response['error'], 'danger')
      else:
        flash('Successful Save Entry.', 'success')
        if published:
          return redirect(url_for('entry_detail', slug=response['data'].get('slug')))
        else:
          return redirect(url_for('edit_entry', slug=response['data'].get('slug')))
  return render_template('blogs/edit_entry.html', meta_title="Edit Entry", entry=entry)

@app.route('/<slug>/', methods=['GET', 'POST'])
def entry_detail(slug):
  response = blog.get_blog_entry_by_slug(slug)
  return render_template('blogs/entry_detail.html', meta_title="Entry Detail", entry=response['data'])

@app.route('/drafts/')
@login_required
def draft_entries():
  current_user = session.get('user')
  response = blog.get_all_draft_entries(current_user.get('id'))
  return render_template('blogs/list_entries.html', meta_title='Draft Blog Entries', entries=response['data'])

@app.route('/published/')
@login_required
def published_entries():
  response = blog.get_all_published_entries(session.get('user').get('id'))
  return render_template('blogs/list_entries.html', meta_title='Published Blog Entries', entries=response['data'])

@app.route('/entries/')
@login_required
def all_entries():
  current_user = session.get('user')
  response = blog.get_all_entries(current_user.get('id'))
  return render_template('blogs/list_entries.html', meta_title="All Blog Entries", entries=response['data'], content_title="Your Blog Entries")

@app.route('/delete_entry?id=<id>')
@login_required
def delete_entry(id):
  entry = None
  with db.get_db_cursor(commit=False) as cur:
    cur.execute("SELECT * FROM entries WHERE id = %s;", (id,))
    entry = cur.fetchone()
  if entry is None:
    flash('Entry Not Found...')
  else:
    if entry['author_id'] != session.get('user').get('id'):
      flash('You do not have authorization to perform task', 'warning')
      abort(403)
    else:
      response = blog.delete_blog_entry(id)
      if response['error']:
        flash('Unable to perform task', 'danger')
        abort(500)
      else:
        flash('You have successfully delete the entry.', 'success')
  return redirect(url_for('all_entries'))

@app.route('/search', methods=['POST'])
def search_entries():
  query = request.form.get('search')
  response = blog.search_entry(query)
  return render_template('search_result.html', entries=response['data'])

@app.errorhandler(404)
def not_found(error):
  return render_template('404.html')

@app.errorhandler(403)
def not_authorized(error):
  return render_template('403.html')

@app.errorhandler(500)
def internal_server_error(error):
  return render_template('500.html')