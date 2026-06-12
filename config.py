import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # поменять
    SECRET_KEY = 'dev-secret-key-change-me-please'

    # SQLite база данных в папке instance/
    SQLALCHEMY_DATABASE_URI = (
        'sqlite:///' + os.path.join(basedir, 'instance', 'library.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Папка для хранения файлов обложек
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'covers')

    # Максимальный размер загружаемого файла - 16 МБ
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Количество книг на одной страниц
    BOOKS_PER_PAGE = 10
