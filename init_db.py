from werkzeug.security import generate_password_hash
import psycopg2
import sys

import os

#def create_tables_and_add_admin
connection = None

try:
    connection = psycopg2.connect(dsn=os.environ['DATABASE_URL'])

    connection.autocommit = True
    
    cursor = connection.cursor()
    
    cursor.execute(open("schema.sql", "r").read())
    #cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s);", ("First Post", "Content for the first post"))
    #cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s);", ("Second Post", "Content for the second post"))
    
    password_hash = generate_password_hash('Owner_Password', method='pbkdf2:sha256')
    cursor.execute("INSERT INTO users (nickname, username, password_hash, email, role) VALUES (%s, %s, %s, %s, %s);", ("Giang Pham", "giangpham", password_hash, "giangpham9500@gmail.com", "owner"))
    print("Done")
except psycopg2.DatabaseError as e:
    print(f'Error {e}')
    sys.exit(1)

finally:
    if connection:
        connection.close()