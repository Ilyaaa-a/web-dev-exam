import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Загружаем переменные окружения из файла .env (если он есть)
load_dotenv(os.path.join(basedir, '.env'))


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ('1', 'true', 'yes', 'on')


class Config:
    # Секретный ключ берём из окружения; дефолт — только для локальной разработки
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me-please')

    # Строка подключения к БД (по умолчанию — SQLite в папке instance/)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or (
        'sqlite:///' + os.path.join(basedir, 'instance', 'library.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Папка для хранения файлов обложек
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(
        basedir, 'static', 'covers'
    )

    # Максимальный размер загружаемого файла - 16 МБ
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    # Количество книг на одной странице
    BOOKS_PER_PAGE = int(os.environ.get('BOOKS_PER_PAGE', 10))

    # Режим отладки (в продакшене должен быть выключен)
    DEBUG = _env_bool('FLASK_DEBUG', False)
