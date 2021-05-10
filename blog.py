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
    cur.execute('UPDATE entries title=%s, content=%s, slug=%s, published=%s RETURNING *;', (title, content, slug, published))
    updated_entry = cur.fetchone()
    cur.execute('UPDATE fts_entries doc_id=%s, search_content=%s;', (doc_id, search_content))
    response['data'] = updated_entry
  return response


def get_all_published_entries(author_id=None):
  response = {'error': None, 'data': None}
  entries = None
  with get_db_cursor() as cur:
    if author_id:
      cur.execute("SELECT title, content, slug, published, created, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE published = %s AND author_id = %s ORDER BY created DESC;", (True, author_id))
    else:
      cur.execute("SELECT title, content, slug, published, created, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE published = %s ORDER BY created DESC;", (True,))
    entries = cur.fetchall()
    response['data'] = entries 
  return response

def get_all_draft_entries(author_id):
  response = {'error': None, 'data': None}
  entries = None
  with get_db_cursor() as cur:
    cur.execute("SELECT title, content, slug, published, created, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE published = %s AND author_id = %s ORDER BY created DESC;", (False, author_id,))
    entries = cur.fetchall()
    response['data'] = entries 
  return response

def get_all_entries(author_id=None):
  response = {'error': None, 'data': None}
  entries = None
  with get_db_cursor() as cur:
    if author_id:
      cur.execute("SELECT title, content, slug, published, created, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE author_id = %s ORDER BY created DESC;", (author_id,))
    else:
      cur.execute("SELECT title, content, slug, published, created, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE ORDER BY created DESC;")
    entries = cur.fetchall()
    response['data'] = entries 
  return response

def get_blog_entry_by_slug(slug):
  response = {'error': None, 'data': None}
  entry = None
  with get_db_cursor() as cur:
    cur.execute("SELECT title, content, slug, published, created, users.nickname as author_name FROM entries INNER JOIN users ON entries.author_id = users.id WHERE slug=%s;", (slug,))
    entry = cur.fetchone()
  
  if entry is None:
    response['error'] = 'Entry Not Found...'
    return response
  else:
    response['data'] = entry
    return response

class BlogManager(object):
  def __init__(self) -> None:
    super().__init__()
    self.response = {'error': None, 'data': None}

  def new_entry(self, entry_data):
    self.response['error'] = None
    if not entry_data['slug']:
      entry_data['slug'] = re.sub('[^\w]+', '-', entry_data['title'].lower())
    search_content = '\n'.join((entry_data['title'], entry_data['content']))
    with get_db_cursor(commit=True) as cur:
      try:
        cur.execute('INSERT INTO entries (title, slug, content, author_id) VALUES (%s, %s, %s, %s) RETURNING id;', (entry_data['title'], entry_data['slug'], entry_data['content'], entry_data['author_id']))
        doc_id = cur.fetchone()[0]
        cur.execute('INSERT INTO fts_entries (doc_id, search_content) VALUES (%s, %s);', (doc_id, search_content))
        self.response['data'] = True
      except Exception:
        self.response['error'] = "Error While Create Blog Entry...."
        return self.response
    
    return self.response

  def update_entry(self, entry_data):
    self.response['error'] = None
    if not entry_data['slug']:
      entry_data['slug'] = re.sub('[^\w]+', '-', entry_data['title'].lower())
    search_content = '\n'.join((entry_data['title'], entry_data['content']))
    with get_db_cursor(commit=True) as cur:
      try:
        cur.execute('UPDATE entries SET title=%s, slug=%s, content=%s, author_id=%s WHERE id=%s;', (entry_data['title'], entry_data['slug'], entry_data['content'], entry_data['author_id'], entry_data['id']))
        cur.execute('UPDATE fts_entries (doc_id, search_content) VALUES (%s, %s);', (entry_data['id'], search_content))
        self.response['data'] = True
      except Exception:
        self.response['error'] = "Error While Update Entry...."
        return self.response
    return self.response

  def get_all_entries(self, published=False):
    self.response['error'] = None
    with get_db_cursor() as cur:
      try:
        cur.execute("SELECT row_to_json(blog_entries) FROM (SELECT * FROM entries WHERE published=%s) AS blog_entries;", (published))
        self.response['data'] = cur.fetchall()
      except Exception:
        self.response['error'] = "Error While Get Entries...."
        return self.response
    return self.response

  def get_single_entries_by_id(self, doc_id):
    self.response['error'] = None
    entry = None
    with get_db_cursor() as cur:
      try:
        cur.execute("SELECT row_to_json(entry) FROM (SELECT * FROM entries WHERE id = %s) AS entry;", (doc_id,))
        entry = cur.fetchone()
      except Exception:
        self.response['error'] = "Error While Get Entry...."
        return self.response
    if entry is None:
      self.response['error'] = "Entry Not Found Or Deleted...."
    else:
      self.response['data'] = entry
    return self.response

  def get_single_entries_by_slug(self, slug):
    self.response['error'] = None
    entry = None
    with get_db_cursor() as cur:
      try:
        cur.execute("SELECT row_to_json(entry) FROM (SELECT * FROM entries WHERE slug = %s) AS entry;", (slug))
        entry = cur.fetchone()
      except Exception:
        self.response['error'] = "Error While Get Entry...."
        return self.response
    if entry is None:
      self.response['error'] = "Entry Not Found Or Deleted...."
    else:
      self.response['data'] = entry
    return self.response

  def delete_entry_by_id(self, doc_id):
    self.response['error'] = None
    with get_db_cursor() as cur:
      try:
        cur.execute("DELETE FROM entries WHERE id = %s;", (doc_id,))
        self.response['data'] = True
      except Exception:
        self.response['error'] = "Error While Delete Entry...."
        return self.response
    return self.response

  def delete_entry_by_slug(self, slug):
    self.response['error'] = None
    with get_db_cursor() as cur:
      try:
        cur.execute("DELETE FROM entries WHERE slug = %s;", (slug,))
        self.response['data'] = True
      except Exception:
        self.response['error'] = "Error While Delete Entry...."
        return self.response
    return self.response