from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)
from flask_login import current_user, login_required

from extensions import db
from models import Book, Review
from utils import sanitize

bp = Blueprint('reviews', __name__)

# Опции для селектора оценки: (значение, подпись)
RATING_OPTIONS = [
    (5, '5 - отлично'),
    (4, '4 - хорошо'),
    (3, '3 - удовлетворительно'),
    (2, '2 - неудовлетворительно'),
    (1, '1 - плохо'),
    (0, '0 - ужасно'),
]


@bp.route('/books/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def create(book_id):
    book = db.get_or_404(Book, book_id)

    # Если пользователь уже оставлял рецензию - перенаправляем на страницу книги
    existing = db.session.scalar(
        db.select(Review).filter_by(book_id=book.id, user_id=current_user.id)
    )
    if existing is not None:
        flash('Вы уже оставляли рецензию на эту книгу', 'info')
        return redirect(url_for('books.view', book_id=book.id))

    if request.method == 'POST':
        rating_raw = request.form.get('rating', '')
        text = request.form.get('text', '').strip()

        valid_ratings = {str(v) for v, _ in RATING_OPTIONS}
        if rating_raw not in valid_ratings or not text:
            flash(
                'При сохранении данных возникла ошибка. '
                'Проверьте корректность введённых данных.',
                'danger',
            )
            return render_template(
                'reviews/form.html', book=book, options=RATING_OPTIONS,
                rating=rating_raw, text=text,
            )

        try:
            review = Review(
                book_id=book.id,
                user_id=current_user.id,
                rating=int(rating_raw),
                text=sanitize(text),
            )
            db.session.add(review)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash(
                'При сохранении данных возникла ошибка. '
                'Проверьте корректность введённых данных.',
                'danger',
            )
            return render_template(
                'reviews/form.html', book=book, options=RATING_OPTIONS,
                rating=rating_raw, text=text,
            )

        flash('Рецензия успешно добавлена', 'success')
        return redirect(url_for('books.view', book_id=book.id))

    return render_template(
        'reviews/form.html', book=book, options=RATING_OPTIONS,
        rating='5', text='',
    )
