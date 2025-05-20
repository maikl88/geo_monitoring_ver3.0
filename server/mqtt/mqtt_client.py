# server/mqtt/mqtt_client.py

import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from server.services.data_service import DataService
from flask import current_app
import sqlite3
import os
from server.config import SQLITE_DB_PATH

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTClient:
    """Клиент MQTT для приема данных с датчиков"""
    
    def __init__(self, app=None, broker_host="localhost", broker_port=1883):
        """
        Инициализация MQTT-клиента
        
        Args:
            app (Flask): Приложение Flask
            broker_host (str): Адрес MQTT-брокера
            broker_port (int): Порт MQTT-брокера
        """
        self.app = app
        self.broker_host = broker_host
        self.broker_port = broker_port
        # Используем новую версию API для устранения предупреждения
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        # Назначаем обработчики
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
    
    def connect(self):
        """Подключение к MQTT-брокеру"""
        try:
            logger.info(f"Подключение к MQTT-брокеру {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к MQTT-брокеру: {e}")
            return False
    
    def disconnect(self):
        """Отключение от MQTT-брокера"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Отключен от MQTT-брокера")
    
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Обработчик события подключения к брокеру"""
        if reason_code == 0:
            logger.info("Успешное подключение к MQTT-брокеру")
            self.connected = True
            
            # Подписываемся на темы для данных с датчиков
            self.client.subscribe("geo/sensors/+/+/data")  # + это wildcard для любого сегмента
            logger.info("Подписка на темы датчиков выполнена")
        else:
            logger.error(f"Не удалось подключиться к MQTT-брокеру, код: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        """Обработчик события отключения от брокера"""
        logger.info(f"Отключение от MQTT-брокера, код: {reason_code}")
        self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Обработчик входящих сообщений"""
        try:
            # Расшифровываем тему сообщения
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 5 and topic_parts[0] == "geo" and topic_parts[1] == "sensors" and topic_parts[4] == "data":
                sensor_type = topic_parts[2]
                sensor_id = int(topic_parts[3])
                
                # Парсим полученное сообщение JSON
                payload = json.loads(msg.payload.decode('utf-8'))
                
                logger.info(f"Получены данные от датчика {sensor_id} ({sensor_type}): {payload}")
                
                # ТОЛЬКО прямая запись SQLite для отладки
                try:
                    # Путь к файлу БД
                    db_path = SQLITE_DB_PATH
                    logger.info(f"Путь к БД для прямой записи: {db_path}")
                    
                    # Проверка существования файла
                    if not os.path.exists(db_path):
                        logger.error(f"Файл БД не существует: {db_path}")
                        return
                    
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Проверка структуры БД
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_reading'")
                    if not cursor.fetchone():
                        logger.error(f"Таблица sensor_reading не существует в БД!")
                        conn.close()
                        return
                    
                    # Проверка количества записей
                    cursor.execute("SELECT COUNT(*) FROM sensor_reading")
                    total_count = cursor.fetchone()[0]
                    logger.info(f"Всего записей в таблице: {total_count}")
                    
                    # Преобразование ISO строки в объект datetime
                    if 'timestamp' in payload:
                        try:
                            timestamp_obj = datetime.fromisoformat(payload['timestamp'])
                        except ValueError:
                            timestamp_obj = datetime.utcnow()
                    else:
                        timestamp_obj = datetime.utcnow()
                    
                    # Форматирование в формат SQLite
                    timestamp_str = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    # Вставляем новую запись
                    cursor.execute(
                        "INSERT INTO sensor_reading (sensor_id, timestamp, value, unit, is_alert) VALUES (?, ?, ?, ?, ?)",
                        (sensor_id, timestamp_str, float(payload['value']), str(payload['unit']), 0)
                    )
                    conn.commit()
                    
                    # Проверяем результат
                    row_id = cursor.lastrowid
                    logger.info(f"Добавлена запись с ID: {row_id}")
                    
                    # Проверяем добавленную запись
                    cursor.execute("SELECT * FROM sensor_reading WHERE id = ?", (row_id,))
                    row = cursor.fetchone()
                    if row:
                        logger.info(f"Проверка записи: {row}")
                    else:
                        logger.error(f"Запись с ID {row_id} не найдена после добавления!")
                    
                    conn.close()
                    logger.info("SQLite: Соединение с БД закрыто")
                    
                except Exception as sqlite_e:
                    logger.error(f"Ошибка прямой записи SQLite: {sqlite_e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    
        except Exception as e:
            logger.error(f"Ошибка обработки MQTT-сообщения: {e}")
            import traceback
            logger.error(traceback.format_exc())

# НЕ создаем глобальный экземпляр здесь - будет создан в init_mqtt