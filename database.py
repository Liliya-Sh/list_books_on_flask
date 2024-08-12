from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship


db = SQLAlchemy()


class Book(db.Model):
    """Свойсва Книги"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    year_of_publication = db.Column(db.Integer)
    number_of_pages = db.Column(db.Integer)
    abstract = db.Column(db.Text(1000), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    added = db.Column(db.DateTime, nullable=False, default=func.now())

    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id", ondelete='SET NULL'))
    genre = relationship("Genre", back_populates="books")

    author_id = db.Column(db.Integer, db.ForeignKey("author.id", ondelete='SET NULL'))
    author = relationship("Author", back_populates="books")

    def __repr__(self):
        return f"Book title(name={self.name!r})"


class Genre(db.Model):
    """Жанр"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)

    books = relationship(
        "Book", back_populates="genre"
    )

    def __repr__(self):
        return f"Genre (name={self.name!r})"


class Author(db.Model):
    """Автор"""
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=True)

    books = relationship(
        "Book", back_populates="author"
    )

    def __repr__(self):
        return f"Author (fullname={self.fullname!r})"
