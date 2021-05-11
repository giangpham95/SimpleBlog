import functools
from flask import session, url_for, redirect, request
from flask.json import jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import urllib
import hashlib
import re

import db

def login_required(fn):
  @functools.wraps(fn)
  def inner(*args, **kwargs):
    if session.get('user'):
      return fn(*args, **kwargs)
    return redirect(url_for('login', next=request.path))
  return inner

def validate_password(password_hash, password):
  return check_password_hash(password_hash, password)

def login_user(login_username, password):
  user = None
  response = {'error': None, 'data': None}
  with db.get_db_cursor(commit=False) as cur:
    cur.execute('SELECT * FROM users WHERE username = %s OR email = %s;', (login_username, login_username,))
    user = cur.fetchone()

  if user is None:
    response['error'] = "Username or Email is not regconized..."
    return response
  
  if not validate_password(user['password_hash'], password):
    response['error'] = "Incorrect Password...."
    return response
  
  response['data'] = user.pop('password_hash')
  return response

def validate_email(email):
  if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
    return False
  return True

def register_user(nickname, username, email, new_pass, new_pass_again, role='subcriber'):
  existing_user = None
  
  response = {'error': None, 'data': None}

  if not validate_email(email):
    response['error'] = "Email is invalid... Please provide a valid email"
    return response

  with db.get_db_cursor(commit=False) as cur:
    cur.execute('SELECT * FROM users WHERE username = %s OR email=%s;', (username,email,))
    existing_user = cur.fetchone()
  
  if existing_user is not None:
    response['error'] = "Username or Email already exist!"
    return response
  
  if new_pass and new_pass_again != new_pass:
    response['error'] = "The retype password do not match...."
    return response

  password_hash = generate_password_hash(new_pass)
  with db.get_db_cursor(commit=True) as cur:
    cur.execute('INSERT INTO users (nickname, username, email, password_hash, role) VALUES (%s, %s, %s, %s, %s);', (nickname, username, email, password_hash, role))
    response['data'] = True
  
  return response

def update_password(username, old_pass, new_pass, new_pass_again):
  response = {'error': None, 'data': None}
  user_current_password = None
  with db.get_db_cursor() as cur:
    cur.execute('SELECT password_hash FROM users WHERE username=%s;', (username,))
    user_current_password = cur.fetchone()
  if user_current_password is None:
    response['error'] = "Username is not regconized!"
    return response
  if not validate_password(user_current_password['password_hash'], old_pass):
    response['error'] = "Incorrect Old Password!!!"
    return response
  if new_pass != new_pass_again:
    response['error'] = "Retype New Password Mismatch..."
    return response
  new_pass_hash = generate_password_hash(new_pass)
  with db.get_db_cursor(commit=True) as cur:
    cur.execute("UPDATE users SET password_hash=%s WHERE username=%s;", (new_pass_hash, username))
    response['data'] = True
  return response

def load_user(username):
  response = {'error': None, 'data': None}
  user = None
  with db.get_db_cursor(commit=False) as cur:
    cur.execute('SELECT * FROM userd WHERE username=%s;', (username,))
    user = cur.fetchone()
  
  if user is None:
    response['error'] = "Unable Load User"
    return response
  else:
    user.pop('password_hash')
    response['data'] = user
    return response

def update_user_profile(old_username, nickname, username, email):
  response = { 'error': None, 'data': None }
  user_with_same_username = None
  user_with_same_email = None
  user_info = None
  with db.get_db_cursor(commit=False) as cur:
    cur.execute('SELECT * FROM users WHERE username=%s;', (username))
    user_with_same_username = cur.fetchone()
    cur.execute('SELECT * FROM users WHERE username=%s;', (old_username))
    user_info = cur.fetchone()
    cur.execute('SELECT * FROM users WHERE email=%s;', (email))
    user_with_same_email = cur.fetchone()
  if user_with_same_username is not None:
    response['error'] = "Username Already Exist!"
    return response
  if user_info is None:
    response['error'] = "User Not Found!"
    return response
  if user_with_same_email['id'] != user_info['id']:
    response['error'] = "Email Already Linked!"
    return response
  with db.get_db_cursor(commit=True) as cur:
    cur.execute("UPDATE users SET nickname=%s, username=%s, email=%s WHERE username=%s;", (nickname, username, email, old_username,))
    response['data'] = True
  return response