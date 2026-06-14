import hashlib
import mimetypes
import os

from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, url_for,
)

from extensions import db
from models import ROLE_ADMIN, ROLE_MODERATOR, Book, Cover, Genre
from utils import render_markdown, role_required, sanitize

bp = Blueprint('books', __name__)

SAVE_ERROR_MESSAGE = (
    'При сохранении данных возникла ошибка. '
    'Проверьте корректность введённых данных.'
)


def _collect_form_data():
    # Считывает поля формы книги в словарь (для сохранения и повторного вывода)
    return {
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'year': request.form.get('year', '').strip(),
        'publisher': request.form.get('publisher', '').strip(),
        'author': request.form.get('author', '').strip(),
        'pages': request.form.get('pages', '').strip(),
        'selected_genre_ids': [
            int(g) for g in request.form.getlist('genres') if g.isdigit()
        ],
    }


def _validate(data):
    # Возвращает True, если все обязательные поля заполнены корректно
    if not all([
        data['title'], data['description'], data['year'],
        data['publisher'], data['author'], data['pages'],
    ]):
        return False
    if not data['year'].isdigit() or not data['pages'].isdigit():
        return False
    if not data['selected_genre_ids']:
        return False
    return True


def _save_cover_file(file, book):
    # Создаёт запись об обложке и сохраняет файл (без дублирования по MD5)
    file_bytes = file.read()
    md5_hash = hashlib.md5(file_bytes).hexdigest()
    # Расширение определяем по MIME-типу (тип, который браузер прислал вместе с файлом)
    # или запасным вариантом - расширение из исходного имени файла
    ext = (
        mimetypes.guess_extension(file.mimetype or '')
        or os.path.splitext(file.filename)[1].lower()
    )
    filename = f'{md5_hash}{ext}'

    cover = Cover(
        filename=filename,
        mime_type=file.mimetype,
        md5_hash=md5_hash,
        book=book,
    )
    db.session.add(cover)

    # Файл сохраняем в файловую систему только если его там ещё нет
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    return file_bytes, path


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(
        db.select(Book).order_by(Book.year.desc(), Book.id.desc()),
        page=page,
        per_page=current_app.config['BOOKS_PER_PAGE'],
        error_out=False,
    )
    return render_template('index.html', pagination=pagination)


@bp.route('/books/<int:book_id>')
def view(book_id):
    book = db.get_or_404(Book, book_id)
    return render_template(
        'books/view.html',
        book=book,
        description_html=render_markdown(book.description),
    )


@bp.route('/books/add', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def add():
    genres = db.session.scalars(db.select(Genre).order_by(Genre.name)).all()

    if request.method == 'POST':
        data = _collect_form_data()
        file = request.files.get('cover')
        has_cover = file is not None and file.filename != ''

        if not _validate(data):
            flash(SAVE_ERROR_MESSAGE, 'danger')
            return render_template(
                'books/form.html', data=data, genres=genres,
                show_cover=True, cover_required=False,
                title='Добавление книги',
            )

        try:
            book = Book(
                title=data['title'],
                description=sanitize(data['description']),
                year=int(data['year']),
                publisher=data['publisher'],
                author=data['author'],
                pages=int(data['pages']),
            )
            book.genres = db.session.scalars(
                db.select(Genre).filter(Genre.id.in_(data['selected_genre_ids']))
            ).all()
            db.session.add(book)
            db.session.flush()  # получаем book.id

            # Обложка необязательна - сохраняем, только если файл приложен
            cover_bytes = cover_path = None
            if has_cover:
                cover_bytes, cover_path = _save_cover_file(file, book)

            db.session.commit()

            # Файл пишем после успешного коммита записей в БД
            if cover_bytes is not None and not os.path.exists(cover_path):
                with open(cover_path, 'wb') as out:
                    out.write(cover_bytes)
        except Exception:
            db.session.rollback()
            flash(SAVE_ERROR_MESSAGE, 'danger')
            return render_template(
                'books/form.html', data=data, genres=genres,
                show_cover=True, cover_required=False,
                title='Добавление книги',
            )

        flash('Книга успешно добавлена', 'success')
        return redirect(url_for('books.view', book_id=book.id))

    return render_template(
        'books/form.html', data=None, genres=genres,
        show_cover=True, cover_required=False, title='Добавление книги',
    )


@bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN, ROLE_MODERATOR)
def edit(book_id):
    book = db.get_or_404(Book, book_id)
    genres = db.session.scalars(db.select(Genre).order_by(Genre.name)).all()

    # Поле обложки показываем только если у книги её ещё нет
    # заменять уже загруженную обложку нельзя
    show_cover = book.cover is None

    if request.method == 'POST':
        data = _collect_form_data()

        if not _validate(data):
            flash(SAVE_ERROR_MESSAGE, 'danger')
            return render_template(
                'books/form.html', data=data, genres=genres,
                show_cover=show_cover, cover_required=False,
                title='Редактирование книги',
            )

        try:
            book.title = data['title']
            book.description = sanitize(data['description'])
            book.year = int(data['year'])
            book.publisher = data['publisher']
            book.author = data['author']
            book.pages = int(data['pages'])
            book.genres = db.session.scalars(
                db.select(Genre).filter(Genre.id.in_(data['selected_genre_ids']))
            ).all()

            # Если обложки не было и пользователь приложил файл - сохраняем
            file = request.files.get('cover')
            cover_bytes = cover_path = None
            if show_cover and file is not None and file.filename != '':
                cover_bytes, cover_path = _save_cover_file(file, book)

            db.session.commit()

            if cover_bytes is not None and not os.path.exists(cover_path):
                with open(cover_path, 'wb') as out:
                    out.write(cover_bytes)
        except Exception:
            db.session.rollback()
            flash(SAVE_ERROR_MESSAGE, 'danger')
            return render_template(
                'books/form.html', data=data, genres=genres,
                show_cover=show_cover, cover_required=False,
                title='Редактирование книги',
            )

        flash('Книга успешно обновлена', 'success')
        return redirect(url_for('books.view', book_id=book.id))

    # GET — заполняет форму данными книги
    data = {
        'title': book.title,
        'description': book.description,
        'year': book.year,
        'publisher': book.publisher,
        'author': book.author,
        'pages': book.pages,
        'selected_genre_ids': [g.id for g in book.genres],
    }
    return render_template(
        'books/form.html', data=data, genres=genres,
        show_cover=show_cover, cover_required=False,
        title='Редактирование книги',
    )


@bp.route('/books/<int:book_id>/delete', methods=['POST'])
@role_required(ROLE_ADMIN)
def delete(book_id):
    book = db.get_or_404(Book, book_id)
    cover = book.cover
    md5_hash = cover.md5_hash if cover else None
    filename = cover.filename if cover else None

    try:
        db.session.delete(book)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('При удалении книги возникла ошибка', 'danger')
        return redirect(url_for('books.index'))

    # Удаляем файл обложки, если на него больше никто не ссылается
    if filename:
        still_used = db.session.scalar(
            db.select(Cover).filter_by(md5_hash=md5_hash)
        )
        if not still_used:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(path):
                os.remove(path)

    flash('Книга успешно удалена', 'success')
    return redirect(url_for('books.index'))
