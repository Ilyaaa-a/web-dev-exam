from functools import wraps

import bleach
import markdown as md
from flask import flash, redirect, url_for
from flask_login import current_user
from markupsafe import Markup

LOGIN_REQUIRED_MESSAGE = (
    'Для выполнения данного действия необходимо пройти процедуру аутентификации'
)
NO_RIGHTS_MESSAGE = 'У вас недостаточно прав для выполнения данного действия'


def role_required(*role_names):
    # Доступ только пользователям с одной из перечисленных ролей.

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(LOGIN_REQUIRED_MESSAGE, 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role.name not in role_names:
                flash(NO_RIGHTS_MESSAGE, 'warning')
                return redirect(url_for('books.index'))
            return view(*args, **kwargs)

        return wrapper

    return decorator


def sanitize(text):
    """Экранирует потенциально опасные теги во введённом пользователем тексте."""
    return bleach.clean(text or '', strip=True)


def render_markdown(text):
    """Преобразует Markdown в безопасный HTML для вывода на странице."""
    html = md.markdown(text or '', extensions=['extra', 'nl2br'])
    return Markup(html)
