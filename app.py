import os
from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import or_
import requests  # For cover image lookup
# SQLAlchemy: ORM we will use to define and manage models.
from data_models import db, Author, Book
from datetime import datetime
from validators import is_valid_name, is_valid_rating, validate_dates, is_valid_year, is_valid_isbn


# Make sure data directory exists
# app = Flask(__name__)
# Get the absolute path to the data directory (one level above Book_Alchemy)
basedir = os.path.dirname(os.path.abspath(__file__)) # dirname replace it with abspath
data_dir = os.path.join(basedir, 'data')  # '..'
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'library.sqlite')
#
app = Flask(__name__)
app.secret_key = 'dev'  # Required for flash messages

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
# SQLite connection.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'

# This will connect the Flask app to the flask-sqlalchemy code.
# Binds database instance to app
db.init_app(app)


with app.app_context():
  db.create_all()

# if os.path.exists("data/library.sqlite"):
#     print("✅ Database file created successfully!")

@app.route('/new_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birth_date_str = request.form.get('birth_date', '').strip()
        death_date_str = request.form.get('date_of_death', '').strip()

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid birth date format.", "error")
            return redirect(url_for('add_author'))

        death_date = None
        if death_date_str:
            try:
                death_date = datetime.strptime(death_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid death date format.", "error")
                return redirect(url_for('add_author'))

        # Validators
        if not is_valid_name(name):
            flash("Invalid author name. Only letters, spaces, hyphens, apostrophes allowed.", "error")
            return redirect(url_for('add_author'))

        is_dates_valid, error_msg = validate_dates(birth_date, death_date)
        if not is_dates_valid:
            flash(error_msg, "error")
            return redirect(url_for('add_author'))

        new_author = Author(name=name, birth_date=birth_date, date_of_death=death_date)
        db.session.add(new_author)
        db.session.commit()
        flash(f"Author {name} added successfully!")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/new_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip()
        pub_year = request.form.get('publication_year', '').strip()
        rating_str = request.form.get('rating', '').strip()
        author_id = request.form.get('author_id')

        # Validations
        if not title:
            flash("Book title is required.", "error")
            return redirect(url_for('add_book'))

        if not is_valid_year(pub_year):
            flash("Invalid publication year.", "error")
            return redirect(url_for('add_book'))

        if not is_valid_isbn(isbn):
            flash("ISBN must be a 13-digit number.", "error")
            return redirect(url_for('add_book'))

        rating = None
        if rating_str:
            try:
                rating = float(rating_str)
                if not is_valid_rating(rating_str):
                    flash("Rating must be between 1.0 and 5.0 stars.", "error")
                    return redirect(url_for('add_book'))
            except ValueError:
                flash("Invalid rating value.", "error")
                return redirect(url_for('add_book'))

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=int(pub_year),
            rating=rating,
            author_id=author_id
        )
        db.session.add(new_book)
        db.session.commit()
        flash(f"Book {title} added successfully!")
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route('/', methods=['GET'])
def home():
    """
    Display books with optional sorting and keyword search.
    - Supports ?sort=title or ?sort=author.
    - Supports ?search=keyword to search book titles and author names.
    """
    sort = request.args.get('sort', 'title')
    keyword = request.args.get('search', '').strip()

    if keyword:
        # Perform case-insensitive search in book title or author name
        books = Book.query.join(Author).filter(
            or_(
                Book.title.ilike(f"%{keyword}%"),
                Author.name.ilike(f"%{keyword}%")
            )
        ).order_by(Book.title).all()

        if not books:
            flash(f"No books found for '{keyword}'")
    else:
        # Default: show all books, sorted
        if sort == 'author':
            books = Book.query.join(Author).order_by(Author.name).all()
        else:
            books = Book.query.order_by(Book.title).all()

    # Add cover images from Open Library
    for book in books:
        book.cover_url = (f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg"
                          if book.isbn else None)

    return render_template('home.html', books=books, sort=sort)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Deletes a book by ID. If the author has no other books left, delete the author too.
    Redirects to the homepage with a success message.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    # Check if the author has any books left.
    remaining_books = Book.query.filter_by(author_id=author.id).count()
    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()
        flash(f"Book {book.title} and author {author.name} deleted.")
    else:
        flash(f"Book {book.title} deleted successfully.")

    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """
    Show detailed information about a specific book.
    """
    book = Book.query.get_or_404(book_id)
    book.cover_url = f"https://covers.openlibrary.org/b/isbn/{book.isbn}-L.jpg" if book.isbn else None
    return render_template('book_detail.html', book=book)


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    """
    Show detailed information about a specific author and their books.
    """
    author = Author.query.get_or_404(author_id)
    return render_template('author_detail.html', author=author)


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """
    Delete an author and all their books.
    """
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash(f"Author {author.name} and all their books were deleted.")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")