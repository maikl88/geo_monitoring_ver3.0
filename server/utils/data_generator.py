# server/utils/data_generator.py (исправленная версия)

import random
from datetime import datetime, timedelta
import math
from server.models.sensor_data import Sensor, Building, AlertConfig
from server.services.data_service import DataService

class DataGenerator:
    """Генератор синтетических данных для тестирования"""
    
    @staticmethod
    def generate_sample_buildings(count=10):
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
    def generate_readings_for_sensor(sensor, days_back=7, readings_per_day=24):
        """
        Генерирует исторические показания для датчика БЕЗ ВРЕМЕННОГО РАЗРЫВА
        
        ВАЖНО: Генерирует данные вплоть до ТЕКУЩЕГО момента, 
        чтобы не было разрыва с данными от симулятора
        """
        readings = []
        
        # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: конечное время = СЕЙЧАС
        end_time = datetime.utcnow()
        
        # Начальное время = days_back дней назад
        start_time = end_time - timedelta(days=days_back)
        
        print(f"Генерация показаний для датчика {sensor.id} ({sensor.name})")
        print(f"Период: {start_time} → {end_time}")
        
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
        total_readings = days_back * readings_per_day
        time_interval = (end_time - start_time) / total_readings
        
        for i in range(total_readings):
            # ВАЖНО: timestamp идет до самого конца (до текущего времени)
            timestamp = start_time + time_interval * i
            
            # Добавляем тренд (медленное изменение со временем)
            trend_factor = i / total_readings
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
            try:
                DataService.add_sensor_reading(
                    sensor_id=sensor.id,
                    value=value,
                    unit=unit,
                    timestamp=timestamp
                )
            except Exception as e:
                print(f"Ошибка добавления показания: {e}")
                continue
                
        print(f"Сгенерировано {total_readings} показаний для датчика {sensor.id}")
    
    @staticmethod
    def cleanup_old_readings(sensor_id, keep_days=30):
        """
        Удаляет старые показания, оставляя только последние keep_days дней
        Полезно для очистки БД от накопившихся данных
        """
        from server.database.db import db
        from server.models.sensor_data import SensorReading
        
        cutoff_time = datetime.utcnow() - timedelta(days=keep_days)
        
        old_readings = SensorReading.query.filter(
            SensorReading.sensor_id == sensor_id,
            SensorReading.timestamp < cutoff_time
        ).all()
        
        count = len(old_readings)
        if count > 0:
            for reading in old_readings:
                db.session.delete(reading)
            
            db.session.commit()
            print(f"Удалено {count} старых показаний для датчика {sensor_id}")
        
        return count
    
    @staticmethod
    def regenerate_recent_data(sensor_id, hours_back=24):
        """
        Пересоздает данные за последние несколько часов
        Полезно для заполнения пробелов в данных
        """
        from server.database.db import db
        from server.models.sensor_data import SensorReading
        
        sensor = DataService.get_sensor(sensor_id)
        if not sensor:
            print(f"Датчик {sensor_id} не найден")
            return
        
        # Удаляем существующие данные за период
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        recent_readings = SensorReading.query.filter(
            SensorReading.sensor_id == sensor_id,
            SensorReading.timestamp >= start_time
        ).all()
        
        for reading in recent_readings:
            db.session.delete(reading)
        
        db.session.commit()
        print(f"Удалены показания за последние {hours_back} часов для датчика {sensor_id}")
        
        # Генерируем новые данные
        days_fraction = hours_back / 24
        DataGenerator.generate_readings_for_sensor(
            sensor, 
            days_back=days_fraction, 
            readings_per_day=24
        )
        
        print(f"Сгенерированы новые показания за последние {hours_back} часов")