from flask import Flask
# SQLAlchemy: ORM we will use to define and manage models.
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

app = Flask(__name__)

# SQLite connection.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'

# This will connect the Flask app to the flask-sqlalchemy code.
# Binds database instance to app
db.init_app(app)

