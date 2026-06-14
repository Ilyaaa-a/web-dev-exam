import os

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config
from extensions import csrf, db, login_manager


@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    # Включаем поддержку внешних ключей в SQLite (для ON DELETE CASCADE)
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Создаём необходимые директории
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from models import User  # noqa
    from utils import render_markdown

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Фильтр Markdown для шаблонов
    app.add_template_filter(render_markdown, name='markdown')

    # Регистрация блюпринтов
    from blueprints.auth import bp as auth_bp
    from blueprints.books import bp as books_bp
    from blueprints.collections import bp as collections_bp
    from blueprints.reviews import bp as reviews_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(reviews_bp)

    return app


app = create_app()


if __name__ == '__main__':
    # Сервер для разработки
    app.run(debug=app.config['DEBUG'])
