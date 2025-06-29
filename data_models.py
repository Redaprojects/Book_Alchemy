from flask_sqlalchemy import SQLAlchemy

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
    name = db.Column(db.String(100))
    birth_date = db.Column(db.String(10), nullable=False)
    date_of_death = db.Column(db.String(10))

    # One-to-many relationship: author has many books
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Author(id=self.id, name={self.name})>"

    def __str__(self):
        return f"{self.name} ({self.birth_date} - {self.date_of_death})"

class Book(db.Model):
    """
    Represents a book in the library.
    Each book belongs to one author.
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Many-to-one relationship: book belongs to one author
    author = db.relationship("Author", back_populates="books")

    def __str__(self):
        return f"{self.title} {self.author.name} ({self.publication_year} - ISBN:{self.isbn})"

    def __repr__(self):
        return (f"<Book id={self.id}, title={self.title}, publication_year={self.publication_year},"
                f" isbn={self.isbn}, author_id={self.author_id})>")
