from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

# Названия ролей (используются для проверки прав доступа)
ROLE_ADMIN = 'administrator'
ROLE_MODERATOR = 'moderator'
ROLE_USER = 'user'


# Соединительная таблица «многие ко многим» между книгами и жанрами
book_genres = db.Table(
    'book_genres',
    db.Column(
        'book_id',
        db.Integer,
        db.ForeignKey('books.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('genres.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


# Соединительная таблица «многие ко многим» между подборками и книгами
collection_books = db.Table(
    'collection_books',
    db.Column(
        'collection_id',
        db.Integer,
        db.ForeignKey('collections.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    db.Column(
        'book_id',
        db.Integer,
        db.ForeignKey('books.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)

    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)   # фамилия
    first_name = db.Column(db.String(64), nullable=False)  # имя
    middle_name = db.Column(db.String(64), nullable=True)  # отчество
    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id'), nullable=False
    )

    role = db.relationship('Role', back_populates='users')
    reviews = db.relationship('Review', back_populates='user')
    collections = db.relationship(
        'Collection',
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name or '']
        return ' '.join(p for p in parts if p).strip()

    # --- Проверки прав доступа ---
    @property
    def is_admin(self):
        return self.role is not None and self.role.name == ROLE_ADMIN

    @property
    def is_moderator(self):
        return self.role is not None and self.role.name == ROLE_MODERATOR

    @property
    def can_create_book(self):
        return self.is_admin

    @property
    def can_edit_book(self):
        return self.is_admin or self.is_moderator

    @property
    def can_delete_book(self):
        return self.is_admin

    @property
    def can_use_collections(self):
        return self.role is not None and self.role.name == ROLE_USER

    def __repr__(self):
        return f'<User {self.login}>'


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)

    books = db.relationship(
        'Book', secondary=book_genres, back_populates='genres'
    )

    def __repr__(self):
        return f'<Genre {self.name}>'


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)        # название
    description = db.Column(db.Text, nullable=False)         # краткое описание
    year = db.Column(db.Integer, nullable=False)            # год
    publisher = db.Column(db.String(256), nullable=False)   # издательство
    author = db.Column(db.String(256), nullable=False)      # автор
    pages = db.Column(db.Integer, nullable=False)           # объём (страниц)

    genres = db.relationship(
        'Genre', secondary=book_genres, back_populates='books'
    )
    cover = db.relationship(
        'Cover',
        back_populates='book',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    reviews = db.relationship(
        'Review',
        back_populates='book',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    def __repr__(self):
        return f'<Book {self.title}>'


class Cover(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)    # название файла
    mime_type = db.Column(db.String(128), nullable=False)   # MIME-тип
    md5_hash = db.Column(db.String(32), nullable=False)     # MD5-хэш
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('books.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
    )

    book = db.relationship('Book', back_populates='cover')

    @property
    def url(self):
        from flask import url_for
        return url_for('static', filename=f'covers/{self.filename}')

    def __repr__(self):
        return f'<Cover {self.filename}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('books.id', ondelete='CASCADE'),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    rating = db.Column(db.Integer, nullable=False)   # оценка 0..5
    text = db.Column(db.Text, nullable=False)        # текст рецензии
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow,
        server_default=func.now(),
    )

    book = db.relationship('Book', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f'<Review book={self.book_id} user={self.user_id}>'


class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User', back_populates='collections')
    books = db.relationship(
        'Book', secondary=collection_books, passive_deletes=True,
    )

    @property
    def book_count(self):
        return len(self.books)

    def __repr__(self):
        return f'<Collection {self.name}>'
