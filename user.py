from db import get_db_cursor
import urllib
import hashlib
import re
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session

# Save User Information to database
def save_user(name, email, password):
  avatar = ''
  with get_db_cursor(commit=True) as cur:
    cur.execute("INSERT INTO users (user_name, user_email, user_password, user_avatar) VALUES (%s, %s, %s, %s);", (name, email, password, avatar))
    return

# Validate Password Hash
def validate_password(password_hash, password):
  return check_password_hash(password_hash, password)

def get_user_by_auth0_id(auth0_id):
  with get_db_cursor(commit=False) as cur:
    cur.execute("SELECT * FROM users WHERE user_auth0_id = %s", (auth0_id))
    user = cur.fetchone()
    return user