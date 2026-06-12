from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Куда перенаправлять неаутентифицированных пользователей
login_manager.login_view = 'auth.login'
login_manager.login_message = (
    'Для выполнения данного действия необходимо пройти процедуру аутентификации'
)
login_manager.login_message_category = 'warning'
