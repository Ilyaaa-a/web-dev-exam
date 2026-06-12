from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
)
from flask_login import login_required, login_user, logout_user

from extensions import db
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = db.session.scalar(
            db.select(User).filter_by(login=login_value)
        )
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('books.index'))

        flash(
            'Невозможно аутентифицироваться с указанными логином и паролем',
            'danger',
        )

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer or url_for('books.index'))
