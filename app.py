import os
from flask import Flask, render_template, request, flash, redirect, url_for
import requests  # For cover image lookup
# SQLAlchemy: ORM we will use to define and manage models.
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book


# Make sure data directory exists
# app = Flask(__name__)
# Get the absolute path to the data directory (one level above Book_Alchemy)
basedir = os.path.dirname(os.path.abspath(__file__)) # dirname replace it with abspath
data_dir = os.path.join(basedir, 'data')  # '..'
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'library.sqlite')
#
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
# SQLite connection.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'

# This will connect the Flask app to the flask-sqlalchemy code.
# Binds database instance to app
db.init_app(app)


# with app.app_context():
#   db.create_all()

# if os.path.exists("data/library.sqlite"):
#     print("✅ Database file created successfully!")

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Route to add a new author to the database.
    GET: Renders form to input author data.
    POST: Extracts form data, saves new Author record to DB,
    flashes a confirmation, and redirects to clear the form.
    """
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form.get('birth_date', None)
        death_date = request.form.get('date_of_death', None)

        new_author = Author(name=name, birth_date= birth_date, date_of_death=death_date)
        db.session.add(new_author)
        db.session.commit()
        flash(f"Author {name} added successfully!")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Add a new book to the database.
    GET: Fetch authors and display form with dropdown.
    POST: Save book data (title, isbn, year, author_id) and flash success.
    """
    authors = Author.query.order_by(Author.name).all()
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        pub_year = request.form.get('publication_year', None)
        author_id = request.form['author_id']

        new_book = Book(title=title, isbn=isbn, publication_year=pub_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()
        flash(f"Book {title} added successfully!")
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route('/', methods=['GET'])
def home():
    """
    Display all books with sorting and cover images.
    Supports ?sort=title or ?sort=author.
    """
    sort = request.args.get('sort', 'title')
    if sort == 'author':
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.order_by(Book.title).all()

    # Fetch cover images using Open Library API (https://covers.openlibrary.org)
    for book in books:
        book.cover_url = (f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg"
                          if book.isbn else None)
    return render_template('home.html', books=books, sort=sort)




if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")