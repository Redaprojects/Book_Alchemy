from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date


# # Create SQLAlchemy object (used in app.py via db.init_app(app))
db = SQLAlchemy()

# db.Model: Base class for models
class Author(db.Model):
    """
    Represents an author in the library.
    Each author can have many books.
    """
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(Date, nullable=False) #db.date
    date_of_death = db.Column(Date)

    # One-to-many relationship: author has many books
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Author(id=self.id, name={self.name})>"

    def __str__(self):
        death = self.date_of_death.strftime('%Y-%m-%d') if self.date_of_death else "Still Alive"
        return f"{self.name} ({self.birth_date.strftime('%Y-%m-%d')} - {death})"


class Book(db.Model):
    """
    Represents a book in the library.
    Each book belongs to one author.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Many-to-one relationship: book belongs to one author
    author = db.relationship("Author", back_populates="books")

    def __str__(self):
        return f"{self.title} {self.author.name} ({self.publication_year} - ISBN:{self.isbn})"

    def __repr__(self):
        return (f"<Book id={self.id}, title={self.title}, publication_year={self.publication_year},"
                f" isbn={self.isbn}, author_id={self.author_id})>")
