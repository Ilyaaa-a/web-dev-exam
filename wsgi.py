"""Точка входа для продакшн-сервера (WSGI).

Запуск с waitress (кросс-платформенно, в т.ч. Windows):
    python wsgi.py
    # или
    waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

Запуск с gunicorn (Linux):
    gunicorn --bind 0.0.0.0:8000 wsgi:app
"""

import os

from app import app

if __name__ == '__main__':
    from waitress import serve

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))
    print(f'Запуск продакшн-сервера на http://{host}:{port}')
    serve(app, host=host, port=port)
