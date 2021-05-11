from db import get_db_cursor
import re

def slugify(title):
  return re.sub('[^\w]+', '-', title.lower())

def generate_search_content(title, content):
  return '\n'.join((title, content))

def new_blog_entry(title, content, author_id, slug=None, published=False):
  response = {'error': None, 'data': None}
  if slug is None:
    slug = slugify(title)
  search_content = generate_search_content(title, content)
  
  existing_entry = None
  with get_db_cursor() as cur:
    cur.execute('SELECT * FROM entries WHERE title = %s;', (title,))
    existing_entry = cur.fetchone()
  
  if existing_entry is not None:
    response['error'] = "There is an entry with the same title...Please choose a new one"
    return response

  # Save to database
  inserted_entry = None
  with get_db_cursor(commit=True) as cur:
    cur.execute('INSERT INTO entries (title, content, author_id, slug, published) VALUES (%s, %s, %s, %s, %s) RETURNING *;', (title, content, author_id, slug, published))
    inserted_entry = cur.fetchone()
    cur.execute('INSERT INTO fts_entries (doc_id, search_content) VALUES (%s, %s);', (inserted_entry['id'], search_content))
    response['data'] = inserted_entry
  return response

def update_blog_entry(doc_id, title, content, published):
  response = {'error': None, 'data': None}
  slug = slugify(title)
  search_content = generate_search_content(title, content)
  
  existing_entry = None
  with get_db_cursor() as cur:
    cur.execute('SELECT * FROM entries WHERE title = %s;', (title,))
    existing_entry = cur.fetchone()
  
  if existing_entry is None:
    response['error'] = "There is no entries with the given slug"
    return response

  # Save to database
  updated_entry = None
  with get_db_cursor(commit=True) as cur:
    cur.execute('UPDATE entries SET title=%s, content=%s, slug=%s, published=%s WHERE id = %s RETURNING *;', (title, content, slug, published, doc_id))
    updated_entry = cur.fetchone()
    cur.execute('UPDATE fts_entries SET search_content=%s WHERE doc_id = %s;', (search_content, doc_id,))
    response['data'] = updated_entry
  return response


def get_all_published_entries(author_id=None):
  response = {'error': None, 'data': None}
  entries = None
  with get_db_cursor() as cur:
    if author_id:
      cur.execute("SELECT entries.id, title, content, slug, published, created, author_id, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE published = %s AND author_id = %s ORDER BY created DESC;", (True, author_id))
    else:
      cur.execute("SELECT entries.id, title, content, slug, published, created, author_id, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE published = %s ORDER BY created DESC;", (True,))
    entries = cur.fetchall()
    response['data'] = entries 
  return response

def get_all_draft_entries(author_id):
  response = {'error': None, 'data': None}
  entries = None
  with get_db_cursor() as cur:
    cur.execute("SELECT entries.id, title, content, slug, published, created, author_id, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE published = %s AND author_id = %s ORDER BY created DESC;", (False, author_id,))
    entries = cur.fetchall()
    response['data'] = entries 
  return response

def get_all_entries(author_id=None):
  response = {'error': None, 'data': None}
  entries = None
  with get_db_cursor() as cur:
    if author_id:
      cur.execute("SELECT entries.id, title, content, slug, published, created, author_id, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE author_id = %s ORDER BY created DESC;", (author_id,))
    else:
      cur.execute("SELECT entries.id, title, content, slug, published, created, author_id, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE ORDER BY created DESC;")
    entries = cur.fetchall()
    response['data'] = entries 
  return response

def get_blog_entry_by_slug(slug):
  response = {'error': None, 'data': None}
  entry = None
  with get_db_cursor() as cur:
    cur.execute("SELECT entries.id, title, content, slug, published, created, author_id, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE slug=%s;", (slug,))
    entry = cur.fetchone()
  
  if entry is None:
    response['error'] = 'Entry Not Found...'
    return response
  else:
    response['data'] = entry
    return response

def delete_blog_entry(doc_id):
  response = {'error': None, 'data': None}
  with get_db_cursor(commit=True) as cur:
    cur.execute("DELETE FROM entries WHERE id = %s;", (doc_id,))
    cur.execute("DELETE FROM fts_entries WHERE doc_id = %s;", (doc_id,))
    response['data'] = True
  return response