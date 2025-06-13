# server/utils/data_generator.py (УПРОЩЕННАЯ ВЕРСИЯ)

import random
from datetime import datetime, timedelta
import math
from server.models.sensor_data import Sensor, Building, AlertConfig
from server.services.data_service import DataService

class DataGenerator:
    """Упрощенный генератор данных"""
    
    @staticmethod
    def generate_sample_buildings(count=5):
        """Создает тестовые здания"""
        buildings = []
        types = ['Жилое', 'Офисное', 'Промышленное']
        
        for i in range(1, count + 1):
            building = Building(
                name=f'Здание {i}',
                address=f'ул. Тестовая, д. {i}',
                floors=random.randint(5, 20),
                construction_year=random.randint(2000, 2020),
                building_type=random.choice(types)
            )
            buildings.append(building)
            
        return buildings
    
    @staticmethod
    def generate_sample_sensors(buildings, count_per_building=3):
        """Создает тестовые датчики"""
        sensors = []
        sensor_types = ['инклинометр', 'тензометр', 'акселерометр', 'датчик трещин', 'датчик температуры']
        
        for building in buildings:
            for i in range(count_per_building):
                sensor_type = random.choice(sensor_types)
                floor = random.randint(1, building.floors) if building.floors else 1
                
                sensor = Sensor(
                    name=f'{sensor_type.capitalize()} {building.name}-{i + 1}',
                    sensor_type=sensor_type,
                    location=f'Этаж {floor}',
                    building_id=building.id,
                    floor=floor,
                    status='active'
                )
                sensors.append(sensor)
                
        return sensors
    
    @staticmethod
    def generate_alert_configs():
        """Создает настройки тревог"""
        configs = [
            AlertConfig(sensor_type='инклинометр', min_threshold=-5, max_threshold=5, unit='градусы'),
            AlertConfig(sensor_type='тензометр', min_threshold=-50, max_threshold=50, unit='мкм/м'),
            AlertConfig(sensor_type='акселерометр', min_threshold=None, max_threshold=20, unit='мм/с²'),
            AlertConfig(sensor_type='датчик трещин', min_threshold=None, max_threshold=5, unit='мм'),
            AlertConfig(sensor_type='датчик температуры', min_threshold=-30, max_threshold=80, unit='°C')
        ]
        return configs
    
    @staticmethod
    def generate_readings_for_sensor(sensor, days_back=2, readings_per_day=24):
        """Генерирует исторические данные БЕЗ разрыва до текущего времени"""
        
        # Базовые значения для разных типов датчиков
        sensor_configs = {
            'инклинометр': {'base': 0, 'unit': 'градусы', 'noise': 0.5},
            'тензометр': {'base': 0, 'unit': 'мкм/м', 'noise': 1.0},
            'акселерометр': {'base': 5, 'unit': 'мм/с²', 'noise': 2.0},
            'датчик трещин': {'base': 0.5, 'unit': 'мм', 'noise': 0.1},
            'датчик температуры': {'base': 20, 'unit': '°C', 'noise': 1.0}
        }
        
        config = sensor_configs.get(sensor.sensor_type, {'base': 0, 'unit': 'единицы', 'noise': 1.0})
        
        # Время: от days_back дней назад до СЕЙЧАС (без разрыва)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        total_readings = days_back * readings_per_day
        time_step = (end_time - start_time) / total_readings
        
        print(f"Генерация для {sensor.name}: {start_time} → {end_time}")
        
        for i in range(total_readings):
            # Время - равномерное распределение до текущего момента
            timestamp = start_time + time_step * i
            
            # Базовое значение + тренд + шум
            trend = (i / total_readings) * config['base'] * 0.1  # Небольшой тренд
            noise = random.uniform(-1, 1) * config['noise']
            
            # Периодические колебания (суточные для температуры)
            periodic = 0
            if sensor.sensor_type == 'датчик температуры':
                hour_factor = timestamp.hour / 24.0 * 2 * math.pi
                periodic = 3 * math.sin(hour_factor)  # ±3°C суточные колебания
            
            value = config['base'] + trend + periodic + noise
            
            # Сохраняем через DataService
            try:
                DataService.add_sensor_reading(
                    sensor_id=sensor.id,
                    value=value,
                    unit=config['unit'],
                    timestamp=timestamp
                )
            except Exception as e:
                print(f"Ошибка сохранения: {e}")
                continue
                
        print(f"Сгенерировано {total_readings} показаний")