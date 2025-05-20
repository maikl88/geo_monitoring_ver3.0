import os

# Определение путей
# Путь к директории server
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
# Путь к корневой директории проекта
BASE_DIR = os.path.dirname(SERVER_DIR)

# Базовые настройки
DEBUG = True
SECRET_KEY = 'dev-key-for-geo-monitoring'  # В реальном проекте нужно использовать безопасный ключ

# Полный путь к базе данных в директории server
DB_PATH = os.path.join(SERVER_DIR, 'geo_monitoring.db')

# Настройки базы данных с абсолютным путем
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Настройки API
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# Путь к базе данных - для прямого доступа через SQLite
# То же самое, что DB_PATH, но экспортируется для использования в других модулях
SQLITE_DB_PATH = DB_PATH

# Настройки MQTT
MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))

# Вывод отладочной информации, если DEBUG включен
if DEBUG:
    print(f"Директория сервера: {SERVER_DIR}")
    print(f"Корневая директория проекта: {BASE_DIR}")
    print(f"Путь к БД SQLite: {DB_PATH}")
    print(f"URI SQLAlchemy: {SQLALCHEMY_DATABASE_URI}")
    print(f"MQTT брокер: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")