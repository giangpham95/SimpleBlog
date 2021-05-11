DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS fts_entries;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  nickname VARCHAR(255) NOT NULL,
  username VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(50) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT UNIQUE NOT NULL,
  content TEXT NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  published BOOLEAN DEFAULT False,
  author_id INT,
  CONSTRAINT fk_user
    FOREIGN KEY(author_id)
      REFERENCES users(id)
);

/* Using for full text search */
CREATE TABLE IF NOT EXISTS fts_entries (
  doc_id INT PRIMARY KEY,
  search_content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
  id SERIAL PRIMARY KEY,
  doc_id INT NOT NULL,
  created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  commenter_id INT NOT NULL,
  CONSTRAINT fk_user
    FOREIGN KEY(commenter_id)
      REFERENCES users(id),
  CONSTRAINT fk_entry
    FOREIGN KEY(doc_id)
      REFERENCES entries(id)
);

/* Create an admin */
