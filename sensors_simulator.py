# sensors_simulator.py (УПРОЩЕННАЯ ВЕРСИЯ)

import time
import json
import random
import math
import argparse
from datetime import datetime
import paho.mqtt.client as mqtt
import sqlite3

class SensorsSimulator:
    """Упрощенный симулятор датчиков"""
    
    def __init__(self, db_path, mqtt_broker, mqtt_port, interval):
        self.db_path = db_path
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.interval = interval
        
        # MQTT клиент
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.connected = False
        
        # Загружаем датчики из БД
        self.sensors = self._load_sensors()
        print(f"Загружено {len(self.sensors)} датчиков")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Обработка подключения"""
        if rc == 0:
            print(f"MQTT подключен к {self.mqtt_broker}:{self.mqtt_port}")
            self.connected = True
        else:
            print(f"MQTT ошибка подключения: {rc}")
    
    def _load_sensors(self):
        """Загружает датчики из БД"""
        sensors = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.id, s.name, s.sensor_type, a.unit
                FROM sensor s
                LEFT JOIN alert_config a ON s.sensor_type = a.sensor_type
                WHERE s.status = 'active'
            """)
            
            for row in cursor.fetchall():
                sensors.append(dict(row))
            
            conn.close()
            
        except Exception as e:
            print(f"Ошибка загрузки датчиков: {e}")
            
        return sensors
    
    def connect(self):
        """Подключение к MQTT"""
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Ошибка подключения MQTT: {e}")
            return False
    
    def disconnect(self):
        """Отключение"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            print("MQTT отключен")
    
    def _generate_value(self, sensor):
        """Генерирует реалистичное значение для датчика"""
        
        # Базовые значения
        sensor_configs = {
            'инклинометр': {'base': 0, 'noise': 0.5, 'range': 3},
            'тензометр': {'base': 0, 'noise': 1.0, 'range': 10},
            'акселерометр': {'base': 5, 'noise': 2.0, 'range': 8},
            'датчик трещин': {'base': 0.5, 'noise': 0.1, 'range': 1},
            'датчик температуры': {'base': 20, 'noise': 1.0, 'range': 10}
        }
        
        config = sensor_configs.get(sensor['sensor_type'], {'base': 0, 'noise': 1, 'range': 5})
        
        # Базовое значение + шум + периодические колебания
        base = config['base']
        noise = random.uniform(-1, 1) * config['noise']
        
        # Периодические изменения (имитация суточного цикла)
        hour = datetime.now().hour
        periodic = math.sin(hour * math.pi / 12) * config['range'] * 0.3
        
        # Медленный тренд (очень малый)
        trend = random.uniform(-0.1, 0.1)
        
        # Иногда аномалии (5% шанс)
        if random.random() < 0.05:
            anomaly = random.uniform(-1, 1) * config['range']
        else:
            anomaly = 0
            
        value = base + noise + periodic + trend + anomaly
        
        return value
    
    def run(self):
        """Запуск симуляции"""
        if not self.sensors:
            print("Нет датчиков для симуляции")
            return
        
        if not self.connect():
            print("Не удалось подключиться к MQTT")
            return
        
        print(f"Симуляция запущена. Интервал: {self.interval} сек")
        
        try:
            while True:
                for sensor in self.sensors:
                    # Генерируем значение
                    value = self._generate_value(sensor)
                    
                    # Создаем сообщение
                    message = {
                        "value": round(value, 2),
                        "unit": sensor['unit'] or 'единицы',
                        "timestamp": datetime.utcnow().isoformat() + 'Z'  # Единый формат
                    }
                    
                    # Тема для MQTT
                    topic = f"geo/sensors/{sensor['sensor_type']}/{sensor['id']}/data"
                    
                    # Отправляем
                    self.client.publish(topic, json.dumps(message))
                    print(f"→ {sensor['name']}: {message['value']} {message['unit']}")
                
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            print("\nСимуляция остановлена")
        finally:
            self.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Симулятор датчиков')
    parser.add_argument('--db', default='server/geo_monitoring.db', help='Путь к БД')
    parser.add_argument('--broker', default='localhost', help='MQTT брокер')
    parser.add_argument('--port', type=int, default=1883, help='MQTT порт')
    parser.add_argument('--interval', type=int, default=10, help='Интервал в секундах')
    
    args = parser.parse_args()
    
    simulator = SensorsSimulator(
        db_path=args.db,
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        interval=args.interval
    )
    
    simulator.run()