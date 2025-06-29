import os
from flask import Flask
# SQLAlchemy: ORM we will use to define and manage models.
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

#
# Get the absolute path to the data directory (one level above Book_Alchemy)
basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, '..', 'data')
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'library.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
# Make sure data directory exists
#
# app = Flask(__name__)
#
# # SQLite connection.
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'

# This will connect the Flask app to the flask-sqlalchemy code.
# Binds database instance to app
db.init_app(app)

with app.app_context():
  db.create_all()

# if os.path.exists("data/library.sqlite"):
#     print("✅ Database file created successfully!")
