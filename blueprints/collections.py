from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)
from flask_login import current_user

from extensions import db
from models import ROLE_USER, Book, Collection
from utils import role_required

bp = Blueprint('collections', __name__, url_prefix='/collections')


@bp.route('/')
@role_required(ROLE_USER)
def index():
    collections = db.session.scalars(
        db.select(Collection)
        .filter_by(user_id=current_user.id)
        .order_by(Collection.name)
    ).all()
    return render_template('collections/index.html', collections=collections)


@bp.route('/<int:collection_id>')
@role_required(ROLE_USER)
def view(collection_id):
    collection = db.get_or_404(Collection, collection_id)
    if collection.user_id != current_user.id:
        flash('У вас недостаточно прав для выполнения данного действия', 'warning')
        return redirect(url_for('collections.index'))
    return render_template('collections/view.html', collection=collection)


@bp.route('/', methods=['POST'])
@role_required(ROLE_USER)
def create():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Название подборки не может быть пустым', 'danger')
        return redirect(url_for('collections.index'))

    try:
        collection = Collection(name=name, user_id=current_user.id)
        db.session.add(collection)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('При создании подборки возникла ошибка', 'danger')
        return redirect(url_for('collections.index'))

    flash('Подборка успешно добавлена', 'success')
    return redirect(url_for('collections.index'))


@bp.route('/add-book/<int:book_id>', methods=['POST'])
@role_required(ROLE_USER)
def add_book(book_id):
    book = db.get_or_404(Book, book_id)
    collection_id = request.form.get('collection_id', '')

    collection = None
    if collection_id.isdigit():
        collection = db.session.get(Collection, int(collection_id))

    if collection is None or collection.user_id != current_user.id:
        flash('Выберите корректную подборку', 'danger')
        return redirect(url_for('books.view', book_id=book.id))

    try:
        if book not in collection.books:
            collection.books.append(book)
            db.session.commit()
            flash('Книга успешно добавлена в подборку', 'success')
        else:
            flash('Эта книга уже есть в выбранной подборке', 'info')
    except Exception:
        db.session.rollback()
        flash('При добавлении книги в подборку возникла ошибка', 'danger')

    return redirect(url_for('books.view', book_id=book.id))
