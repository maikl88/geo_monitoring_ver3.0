# server/config.py

import os

# Базовые настройки
DEBUG = True
SECRET_KEY = 'dev-key-for-geo-monitoring'  # В реальном проекте нужно использовать безопасный ключ

# Настройки базы данных
SQLALCHEMY_DATABASE_URI = 'sqlite:///geo_monitoring.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Настройки API
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# Путь к базе данных
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geo_monitoring.db')