from contextlib import contextmanager
import logging
import os
from typing import NamedTuple

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

pool = None

def setup():
  global pool
  DATABASE_URL = os.environ['DATABASE_URL']
  current_app.logger.info(f"creating db connection pool")
  pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
  try:
    connection = pool.getconn()
    yield connection
  finally:
    pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
  with get_db_connection() as connection:
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    # cursor = connection.cursor()
    try:
      yield cursor
      if commit:
        connection.commit()
    finally:
      cursor.close()