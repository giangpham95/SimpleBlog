import functools
from flask import session, url_for, redirect, request
from flask.json import jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import urllib
import hashlib
import re
import psycopg2

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
  
  response['data'] = user
  return response

def validate_email(email):
  if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
    return False
  return True

def register_user(nickname, username, email, new_pass, new_pass_again, role='subcriber'):
  users_with_same_name = None
  users_with_same_email = None
  
  response = {'error': None, 'data': None}

  if not validate_email(email):
    response['error'] = "Email is invalid... Please provide a valid email"
    return response

  with db.get_db_cursor(commit=False) as cur:
    cur.execute('SELECT * FROM users WHERE username = %s;', (username,))
    users_with_same_name = cur.fetchone()
  
  if users_with_same_name is not None:
    response['error'] = "Username already exist! Please choose other one!"
    return response
  
  if new_pass and new_pass_again != new_pass:
    response['error'] = "The retype password do not match...."
    return response

  password_hash = generate_password_hash(new_pass)
  with db.get_db_cursor(commit=True) as cur:
    cur.execute('INSERT INTO users (nickname, username, email, password_hash, role) VALUES (%s, %s, %s, %s, %s);', (nickname, username, email, password_hash, role))
    response['data'] = True
  
  return response