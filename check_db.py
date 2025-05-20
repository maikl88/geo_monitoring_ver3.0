# check_db.py (создайте в корне проекта)
import os
from server.config import SQLALCHEMY_DATABASE_URI, SQLITE_DB_PATH

print(f"SQLAlchemy URI: {SQLALCHEMY_DATABASE_URI}")
print(f"SQLite прямой путь: {SQLITE_DB_PATH}")

if os.path.exists(SQLITE_DB_PATH):
    print(f"Файл БД существует: {SQLITE_DB_PATH}")
    print(f"Размер: {os.path.getsize(SQLITE_DB_PATH)} байт")
else:
    print(f"Файл БД не существует: {SQLITE_DB_PATH}")