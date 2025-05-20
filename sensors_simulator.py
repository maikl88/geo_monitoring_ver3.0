# sensors_simulator.py

import time
import json
import random
import math
import argparse
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import sqlite3
import os

# Настройки по умолчанию
DEFAULT_DB_PATH = 'server/geo_monitoring.db'
DEFAULT_MQTT_BROKER = 'localhost'
DEFAULT_MQTT_PORT = 1883
DEFAULT_INTERVAL = 10  # секунд между отправками данных

class SensorsSimulator:
    """Имитатор данных с датчиков через MQTT"""
    
    def __init__(self, db_path, mqtt_broker, mqtt_port, interval):
        """
        Инициализация имитатора
        
        Args:
            db_path (str): Путь к файлу базы данных SQLite
            mqtt_broker (str): Адрес MQTT-брокера
            mqtt_port (int): Порт MQTT-брокера
            interval (int): Интервал отправки данных в секундах
        """
        self.db_path = db_path
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.interval = interval
        
        # Инициализация MQTT-клиента
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.connected = False
        
        # Загрузка информации о датчиках из БД
        self.sensors = self._load_sensors_from_db()
        print(f"Загружено {len(self.sensors)} датчиков из БД")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Обработчик подключения к брокеру"""
        if rc == 0:
            print(f"Подключено к MQTT-брокеру {self.mqtt_broker}:{self.mqtt_port}")
            self.connected = True
        else:
            print(f"Ошибка подключения к MQTT-брокеру, код: {rc}")
    
    def _load_sensors_from_db(self):
        """Загружает информацию о датчиках из базы данных"""
        sensors = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Выбираем все активные датчики
            cursor.execute("""
                SELECT s.id, s.name, s.sensor_type, s.building_id, s.floor, 
                       a.min_threshold, a.max_threshold, a.unit
                FROM sensor s
                LEFT JOIN alert_config a ON s.sensor_type = a.sensor_type
                WHERE s.status = 'active'
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                sensors.append(dict(row))
            
            conn.close()
            return sensors
            
        except Exception as e:
            print(f"Ошибка загрузки датчиков из БД: {e}")
            return []
    
    def connect(self):
        """Подключение к MQTT-брокеру"""
        try:
            print(f"Подключение к MQTT-брокеру {self.mqtt_broker}:{self.mqtt_port}")
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Ошибка подключения к MQTT-брокеру: {e}")
            return False
    
    def disconnect(self):
        """Отключение от MQTT-брокера"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            print("Отключен от MQTT-брокера")
    
    def _generate_sensor_value(self, sensor):
        """
        Генерирует правдоподобное значение для датчика
        
        Args:
            sensor (dict): Информация о датчике
            
        Returns:
            float: Сгенерированное значение
        """
        # Базовое значение по умолчанию
        base_value = 0
        
        # Определяем базовое значение в зависимости от типа датчика
        if sensor['sensor_type'] == 'инклинометр':
            base_value = 0  # Базовый наклон 0 градусов
        elif sensor['sensor_type'] == 'тензометр':
            base_value = 0  # Базовая деформация 0 мкм/м
        elif sensor['sensor_type'] == 'акселерометр':
            base_value = 5  # Базовая вибрация 5 мм/с²
        elif sensor['sensor_type'] == 'датчик трещин':
            base_value = 0.5  # Базовая ширина трещины 0.5 мм
        elif sensor['sensor_type'] == 'датчик температуры':
            base_value = 20  # Базовая температура 20°C
        
        # Добавляем случайное отклонение
        noise_factor = 0.5
        if sensor['sensor_type'] == 'акселерометр':
            noise_factor = 2  # Акселерометры более шумные
        
        noise = random.uniform(-1, 1) * noise_factor
        
        # Добавляем периодические колебания (например, для температуры)
        periodic = 0
        hour_of_day = datetime.now().hour
        
        if sensor['sensor_type'] == 'датчик температуры':
            periodic = 5 * math.sin(hour_of_day * math.pi / 12)  # ±5°C в течение дня
        elif sensor['sensor_type'] == 'акселерометр':
            # Больше вибраций в рабочие часы
            if 8 <= hour_of_day <= 18:
                periodic = 5
        
        # Добавляем медленный тренд
        trend = 0
        # В реальном приложении можно хранить и обновлять состояние трендов
        
        # Итоговое значение
        value = base_value + trend + periodic + noise
        
        # Иногда генерируем аномальные значения (для проверки системы тревог)
        if random.random() < 0.05:  # 5% шанс аномалии
            if sensor['min_threshold'] is not None and sensor['max_threshold'] is not None:
                # Генерируем значение за пределами порогов
                if random.random() < 0.5:
                    value = sensor['min_threshold'] - random.uniform(1, 5)
                else:
                    value = sensor['max_threshold'] + random.uniform(1, 5)
        
        return value
    
    def run(self):
        """Запускает процесс имитации данных датчиков"""
        if not self.sensors:
            print("Нет активных датчиков для имитации")
            return
        
        if not self.connect():
            print("Не удалось подключиться к MQTT-брокеру. Остановка имитации.")
            return
        
        print(f"Начало имитации данных с датчиков. Интервал: {self.interval} сек.")
        
        try:
            while True:
                for sensor in self.sensors:
                    # Генерируем значение для датчика
                    value = self._generate_sensor_value(sensor)
                    
                    # Создаем сообщение
                    message = {
                        "value": value,
                        "unit": sensor['unit'],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Формируем тему для отправки
                    topic = f"geo/sensors/{sensor['sensor_type']}/{sensor['id']}/data"
                    
                    # Публикуем сообщение
                    self.client.publish(topic, json.dumps(message))
                    print(f"Отправлены данные в {topic}: {message}")
                
                # Ждем до следующего цикла
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            print("Имитация остановлена пользователем")
        finally:
            self.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Имитатор датчиков для системы геотехнического мониторинга')
    parser.add_argument('--db', default=DEFAULT_DB_PATH, help=f'Путь к файлу базы данных (по умолчанию: {DEFAULT_DB_PATH})')
    parser.add_argument('--broker', default=DEFAULT_MQTT_BROKER, help=f'Адрес MQTT-брокера (по умолчанию: {DEFAULT_MQTT_BROKER})')
    parser.add_argument('--port', type=int, default=DEFAULT_MQTT_PORT, help=f'Порт MQTT-брокера (по умолчанию: {DEFAULT_MQTT_PORT})')
    parser.add_argument('--interval', type=int, default=DEFAULT_INTERVAL, help=f'Интервал отправки данных в секундах (по умолчанию: {DEFAULT_INTERVAL})')
    
    args = parser.parse_args()
    
    simulator = SensorsSimulator(
        db_path=args.db,
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        interval=args.interval
    )
    
    simulator.run()