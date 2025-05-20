# test_db_write.py
import sqlite3
import datetime
import os

DB_PATH = '/home/maikl/Python_projects/geo_monitoring/server/geo_monitoring.db'

def test_write():
    print(f"Тестовая запись в БД: {DB_PATH}")
    
    # Проверка существования файла
    if not os.path.exists(DB_PATH):
        print(f"Ошибка: файл базы данных не существует")
        return
    
    # Проверка доступа для записи
    if not os.access(DB_PATH, os.W_OK):
        print(f"Ошибка: нет прав на запись в файл базы данных")
        return
    
    try:
        # Подключение к БД с таймаутом
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        cursor = conn.cursor()
        
        # Проверка структуры
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_reading'")
        if not cursor.fetchone():
            print("Ошибка: таблица sensor_reading не существует")
            conn.close()
            return
        
        # Создаем тестовую запись
        now = datetime.datetime.now()
        timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        test_value = 999.99  # Значение, которое легко найти для проверки
        
        # Запись в БД
        cursor.execute(
            "INSERT INTO sensor_reading (sensor_id, timestamp, value, unit, is_alert) VALUES (?, ?, ?, ?, ?)",
            (1, timestamp_str, test_value, "test", 0)
        )
        conn.commit()
        
        # Проверка записи
        last_id = cursor.lastrowid
        print(f"Запись добавлена с ID: {last_id}")
        
        # Проверяем, что запись действительно добавлена
        cursor.execute("SELECT * FROM sensor_reading WHERE id = ?", (last_id,))
        row = cursor.fetchone()
        if row:
            print(f"Проверка записи: {row}")
        else:
            print(f"Ошибка: запись с ID {last_id} не найдена после добавления")
        
        # Подсчитываем общее количество записей
        cursor.execute("SELECT COUNT(*) FROM sensor_reading")
        count = cursor.fetchone()[0]
        print(f"Всего записей в таблице sensor_reading: {count}")
        
        conn.close()
        print("Тест завершен успешно")
        
    except Exception as e:
        print(f"Ошибка при работе с БД: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_write()