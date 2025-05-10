# server/database/db.py

from flask_sqlalchemy import SQLAlchemy

# Инициализация объекта SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Инициализирует базу данных с приложением Flask
    """
    db.init_app(app)
    
    # Создает все таблицы, если их нет
    with app.app_context():
        db.create_all()
        print("База данных инициализирована!")