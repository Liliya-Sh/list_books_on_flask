import os

from flask import Flask, render_template, request, redirect, flash
import re

from database import Book, Genre, Author, db
from data import fill_db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///list_books.db'
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)

# Создаем таблицы
with app.app_context():
    db.drop_all()
    db.create_all()
    fill_db() #Добавляем данные в БД


@app.route("/")
def all_books():
    """Просмотреть список всех книг"""
    query = db.select(Book).order_by(Book.added.desc()).limit(15)
    books = db.session.execute(query).scalars().all()
    # books = Book.query.all()

    return render_template("all_books.html", books=books)


@app.route("/book/<int:book_id>/")
def book_detail(book_id):
    """Просмотреть книгу по id"""
    book = db.get_or_404(Book, ident=book_id)
    if not book:
        return 'Книга не найдена'

    return render_template("book.html", book=book)


@app.route("/all_genres/")
def all_genres():
    """Просмотреть список всех жанров"""
    genres = Genre.query.all()
    return render_template("all_genres.html", genres=genres)


@app.route("/all_authors/")
def all_authors():
    """Просмотреть список всех авторов"""
    authors = Author.query.all()
    return render_template("all_authors.html", authors=authors)


@app.route("/genre/<int:genre_id>/")
def books_by_genre(genre_id):
    """Просмотреть список всех книг по жанру"""
    genre = Genre.query.get_or_404(genre_id)
    if not genre:
        return 'Жанр не найден'
    return render_template(
        "books_by_genre.html",
        genre_name=genre.name,
        books=genre.books
    )


@app.route("/author/<int:author_id>/")
def books_by_author(author_id):
    """Просмотреть список всех книг по автору"""
    author = Author.query.get_or_404(author_id)
    if not author:
        return 'Автор не найден'
    return render_template(
        "books_by_author.html",
        author_fullname=author.fullname,
        books=author.books
    )


@app.route("/read_status/<int:book_id>/", methods=['POST'])
def read_status(book_id):
    """Меняем статус книги на 'прочитанный' или 'не прочитанный'"""
    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()
        book.is_read = not book.is_read
        db.session.commit()

        return redirect(request.referrer)


@app.route("/add_book/", methods=['GET', 'POST'])
def add_book():
    """Добавить новую книгу"""

    if request.method == "POST":
        # Проверка введенных данных
        errors = validate_book_form(request.form)
        if errors:
            for error in errors:
                flash(error, category='error')
            return render_template("add_book.html")

        book_name = request.form["name"]
        author_name = request.form["author"]
        genre_name = request.form["genre"]
        abstract = request.form["abstract"]
        year_of_publication = request.form.get("year_of_publication", None)
        number_of_pages = request.form.get("number_of_pages", None)

        # Проверяем есть ли такая книга
        existing_book = Book.query.filter_by(name=book_name).first()
        if existing_book:
            flash("Книга с таким именем уже существует!", category='error')
            return render_template("add_book.html"), 400

        # Проверяем есть ли такой автор, если нет добавляем
        author = Author.query.filter_by(fullname=author_name).first()
        if not author:
            author = Author(fullname=author_name)
            db.session.add(author)

        # Проверяем есть ли такой жанр, если нет добавляем
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)

        # Добавляем книгу, если ее нет в списке
        book = Book(
            name=book_name,
            author=author,
            genre=genre,
            abstract=abstract,
            year_of_publication=year_of_publication,
            number_of_pages=number_of_pages,
        )
        db.session.add(book)

        try:
            db.session.commit()
            flash("Книга успешно добавлена!", category='success')
            return render_template("add_book.html")

        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при добавлении книги: {e}")
            flash("Ошибка при добавлении книги", category='error')
            return render_template("add_book.html"), 500

    return render_template("add_book.html")


def validate_book_form(form):
    """Задаем условия для данных, которые будут вводить"""
    errors = []
    if not form.get("name") or len(form["name"]) > 50:
        errors.append("Название книги введено неверно")
    if not form.get("author"):
        errors.append("Необходимо указать автора")
    if not form.get("genre"):
        errors.append("Необходимо указать жанр")
    if not form.get("abstract") or len(form["abstract"]) > 500:
        errors.append("Аннотация должна содержать до 500 символов")
    if form.get("year_of_publication") and not re.match(r'^\d+$', form["year_of_publication"]):
        errors.append("Год публикации должно быть числовым значением")
    if form.get("number_of_pages") and not re.match(r'^\d+$', form["number_of_pages"]):
        errors.append("Количество страниц должно быть числовым значением")

    return errors


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
