import psycopg2

import os

connection = psycopg2.connect(dsn=os.environ['DATABASE_URL'])

cursor = connection.cursor()

cursor.execute(open("schema.sql", "r").read())

#cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s);", ("First Post", "Content for the first post"))

#cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s);", ("Second Post", "Content for the second post"))

connection.commit()

cursor.close()

print("Done")