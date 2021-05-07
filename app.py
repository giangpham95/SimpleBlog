from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.heroku import Heroku

app = Flask(__name__)
heroku = Heroku(app)
db = SQLAlchemy(app)

@app.route('/')
def index():
  return render_template('index.html')