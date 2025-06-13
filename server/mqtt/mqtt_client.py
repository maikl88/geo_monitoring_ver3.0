# server/mqtt/mqtt_client.py (ИСПРАВЛЕННАЯ ВЕРСИЯ с контекстом)

import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import sqlite3
import os
from server.config import SQLITE_DB_PATH

logger = logging.getLogger(__name__)

class MQTTClient:
    """MQTT клиент с прямой записью в БД (без Flask контекста)"""
    
    def __init__(self, app=None, broker_host="localhost", broker_port=1883):
        self.app = app
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        # Обработчики событий
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
    
    def connect(self):
        """Подключение к MQTT брокеру"""
        try:
            logger.info(f"Подключение к MQTT {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения MQTT: {e}")
            return False
    
    def disconnect(self):
        """Отключение"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT отключен")
    
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Обработка подключения"""
        if reason_code == 0:
            logger.info("MQTT подключен успешно")
            self.connected = True
            # Подписка на все темы датчиков
            self.client.subscribe("geo/sensors/+/+/data")
            logger.info("Подписка на темы датчиков выполнена")
        else:
            logger.error(f"MQTT подключение не удалось: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        """Обработка отключения"""
        logger.info(f"MQTT отключен: {reason_code}")
        self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Обработка входящих сообщений - ПРЯМАЯ ЗАПИСЬ В БД"""
        try:
            # Парсим тему: geo/sensors/тип/id/data
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 5:
                sensor_id = int(topic_parts[3])
                
                # Парсим JSON
                payload = json.loads(msg.payload.decode('utf-8'))
                logger.info(f"MQTT → Датчик {sensor_id}: {payload}")
                
                # Парсим время
                timestamp_str = payload.get('timestamp', datetime.utcnow().isoformat() + 'Z')
                # Убираем Z и конвертируем в SQLite формат
                clean_time = timestamp_str.replace('Z', '')
                try:
                    dt = datetime.fromisoformat(clean_time)
                    sqlite_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                except:
                    sqlite_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                
                # ПРЯМАЯ ЗАПИСЬ В SQLITE (БЕЗ Flask контекста)
                self._save_to_database(
                    sensor_id=sensor_id,
                    timestamp=sqlite_timestamp,
                    value=float(payload['value']),
                    unit=str(payload['unit'])
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки MQTT сообщения: {e}")
    
    def _save_to_database(self, sensor_id, timestamp, value, unit):
        """Прямое сохранение в SQLite без Flask контекста"""
        try:
            # Проверяем путь к БД
            if not os.path.exists(SQLITE_DB_PATH):
                logger.error(f"БД не найдена: {SQLITE_DB_PATH}")
                return
            
            # Подключаемся к БД
            conn = sqlite3.connect(SQLITE_DB_PATH, timeout=10.0)
            cursor = conn.cursor()
            
            # Проверяем, что датчик существует
            cursor.execute("SELECT sensor_type FROM sensor WHERE id = ?", (sensor_id,))
            sensor_row = cursor.fetchone()
            
            if not sensor_row:
                logger.warning(f"Датчик {sensor_id} не найден в БД")
                conn.close()
                return
            
            sensor_type = sensor_row[0]
            
            # Проверяем пороги тревоги
            is_alert = 0
            cursor.execute(
                "SELECT min_threshold, max_threshold FROM alert_config WHERE sensor_type = ?", 
                (sensor_type,)
            )
            alert_row = cursor.fetchone()
            
            if alert_row:
                min_threshold, max_threshold = alert_row
                if min_threshold is not None and value < min_threshold:
                    is_alert = 1
                if max_threshold is not None and value > max_threshold:
                    is_alert = 1
            
            # Вставляем запись
            cursor.execute(
                "INSERT INTO sensor_reading (sensor_id, timestamp, value, unit, is_alert) VALUES (?, ?, ?, ?, ?)",
                (sensor_id, timestamp, value, unit, is_alert)
            )
            
            conn.commit()
            row_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"✓ Сохранено: датчик {sensor_id}, значение {value} {unit}, ID записи {row_id}")
            
        except Exception as e:
            logger.error(f"Ошибка записи в БД: {e}")
            if 'conn' in locals():
                conn.close()