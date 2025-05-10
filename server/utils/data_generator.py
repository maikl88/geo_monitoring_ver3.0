# server/utils/data_generator.py

import random
from datetime import datetime, timedelta
import math
from server.models.sensor_data import Sensor, Building, AlertConfig
from server.services.data_service import DataService

class DataGenerator:
    """Генератор синтетических данных для тестирования"""
    
    @staticmethod
    def generate_sample_buildings(count=2):
        """Создает тестовые здания"""
        buildings = []
        building_types = ['Жилое', 'Офисное', 'Промышленное']
        
        for i in range(1, count + 1):
            building = Building(
                name=f'Здание {i}',
                address=f'ул. Примерная, д. {i}',
                floors=random.randint(5, 30),
                construction_year=random.randint(1990, 2020),
                building_type=random.choice(building_types)
            )
            buildings.append(building)
            
        return buildings
    
    @staticmethod
    def generate_sample_sensors(buildings, count_per_building=5):
        """Создает тестовые датчики для зданий"""
        sensors = []
        sensor_types = ['инклинометр', 'тензометр', 'акселерометр', 'датчик трещин', 'датчик температуры']
        
        for building in buildings:
            for i in range(count_per_building):
                sensor_type = random.choice(sensor_types)
                floor = random.randint(1, building.floors) if building.floors else None
                
                sensor = Sensor(
                    name=f'{sensor_type.capitalize()} {building.name} {i + 1}',
                    sensor_type=sensor_type,
                    location=f'Этаж {floor}, {random.choice(["северная", "южная", "западная", "восточная"])} сторона',
                    building_id=building.id,
                    floor=floor,
                    position_x=random.uniform(0, 100),
                    position_y=random.uniform(0, 100),
                    status='active'
                )
                sensors.append(sensor)
                
        return sensors
    
    @staticmethod
    def generate_alert_configs():
        """Создает настройки тревог для разных типов датчиков"""
        configs = [
            AlertConfig(sensor_type='инклинометр', min_threshold=-5, max_threshold=5, unit='градусы'),
            AlertConfig(sensor_type='тензометр', min_threshold=-50, max_threshold=50, unit='мкм/м'),
            AlertConfig(sensor_type='акселерометр', min_threshold=None, max_threshold=20, unit='мм/с²'),
            AlertConfig(sensor_type='датчик трещин', min_threshold=None, max_threshold=5, unit='мм'),
            AlertConfig(sensor_type='датчик температуры', min_threshold=-30, max_threshold=80, unit='°C')
        ]
        return configs
    
    @staticmethod
    def generate_readings_for_sensor(sensor, days_back=30, readings_per_day=24):
        """Генерирует исторические показания для датчика"""
        readings = []
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        # Определяем базовое значение и единицу измерения в зависимости от типа датчика
        base_value = 0
        unit = 'единицы'
        
        if sensor.sensor_type == 'инклинометр':
            base_value = 0  # Начальный наклон 0 градусов
            unit = 'градусы'
        elif sensor.sensor_type == 'тензометр':
            base_value = 0  # Начальная деформация 0 мкм/м
            unit = 'мкм/м'
        elif sensor.sensor_type == 'акселерометр':
            base_value = 5  # Базовая вибрация 5 мм/с²
            unit = 'мм/с²'
        elif sensor.sensor_type == 'датчик трещин':
            base_value = 0.5  # Начальная ширина трещины 0.5 мм
            unit = 'мм'
        elif sensor.sensor_type == 'датчик температуры':
            base_value = 20  # Начальная температура 20°C
            unit = '°C'
        
        # Генерируем значения с некоторым трендом и случайными колебаниями
        time_interval = (end_time - start_time) / (days_back * readings_per_day)
        
        for i in range(days_back * readings_per_day):
            timestamp = start_time + time_interval * i
            
            # Добавляем тренд (медленное изменение со временем)
            trend_factor = i / (days_back * readings_per_day)
            trend = 0
            
            if sensor.sensor_type == 'инклинометр':
                trend = trend_factor * 3  # Медленное увеличение наклона
            elif sensor.sensor_type == 'тензометр':
                trend = trend_factor * 20  # Медленное увеличение деформации
            elif sensor.sensor_type == 'датчик трещин':
                trend = trend_factor * 2  # Медленное увеличение ширины трещины
            
            # Добавляем периодические колебания (например, день-ночь для температуры)
            hour_of_day = timestamp.hour
            periodic = 0
            
            if sensor.sensor_type == 'датчик температуры':
                periodic = 5 * math.sin(hour_of_day * math.pi / 12)  # ±5°C в течение дня
            elif sensor.sensor_type == 'акселерометр':
                # Больше вибраций в рабочие часы
                if 8 <= hour_of_day <= 18:
                    periodic = 5
            
            # Добавляем случайный шум
            noise = random.uniform(-1, 1)
            noise_factor = 0.5
            
            if sensor.sensor_type == 'акселерометр':
                noise_factor = 2  # Акселерометры более шумные
            
            # Итоговое значение
            value = base_value + trend + periodic + (noise * noise_factor)
            
            # Создаем показание
            DataService.add_sensor_reading(
                sensor_id=sensor.id,
                value=value,
                unit=unit,
                timestamp=timestamp
            )