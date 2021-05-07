from db import get_db_cursor
from werkzeug.exceptions import abort


def create_post(title, content):
  with get_db_cursor(commit=True) as cur:
    cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s);", (title, content))
    return

def get_all_posts():
  with get_db_cursor(commit=False) as cur:
    cur.execute("SELECT * FROM posts")
    return cur.fetchall()

def get_post(post_id):
  with get_db_cursor(commit=False) as cur:
    cur.execute("SELECT * FROM posts WHERE id = %s;", (post_id, ))
    post = cur.fetchone()
    return post

def update_post(id, title, content):
  with get_db_cursor(commit=True) as cur:
    cur.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s;", (title, content, id,))
    return

def delete_post(id):
  with get_db_cursor(commit=True) as cur:
    cur.execute("DELETE FROM posts WHERE id = %s;", (id,))
    return