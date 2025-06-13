# server/services/data_service.py (исправленная версия с отладкой)

from datetime import datetime, timedelta
from server.database.db import db
from server.models.sensor_data import Sensor, SensorReading, Building, AlertConfig
import pytz

class DataService:
    """Сервис для работы с данными датчиков"""
    
    @staticmethod
    def get_all_buildings():
        """Получить все здания"""
        return Building.query.all()
    
    @staticmethod
    def get_building(building_id):
        """Получить конкретное здание по ID"""
        return Building.query.get(building_id)
    
    @staticmethod
    def get_sensors_for_building(building_id):
        """Получить все датчики для конкретного здания"""
        return Sensor.query.filter_by(building_id=building_id).all()
    
    @staticmethod
    def get_sensor(sensor_id):
        """Получить конкретный датчик по ID"""
        return Sensor.query.get(sensor_id)
    
    @staticmethod
    def get_latest_readings(sensor_id, limit=1):
        """Получить последние показания датчика"""
        return SensorReading.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorReading.timestamp.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_readings_for_period(sensor_id, start_time, end_time=None):
        """
        Получить показания датчика за определенный период
        С улучшенной обработкой времени и отладкой
        """
        if end_time is None:
            end_time = datetime.utcnow()
        
        # Добавляем отладочную информацию
        print(f"=== ОТЛАДКА DataService.get_readings_for_period ===")
        print(f"Sensor ID: {sensor_id}")
        print(f"Start time: {start_time}")
        print(f"End time: {end_time}")
        
        # Сначала получаем ВСЕ данные для этого датчика для понимания ситуации
        all_readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorReading.timestamp.desc())\
            .limit(100).all()  # Последние 100 записей
        
        print(f"Всего записей для датчика {sensor_id}: {len(all_readings)}")
        
        if all_readings:
            latest_time = all_readings[0].timestamp
            oldest_time = all_readings[-1].timestamp if len(all_readings) > 1 else latest_time
            print(f"Самая новая запись: {latest_time}")
            print(f"Самая старая из последних 100: {oldest_time}")
            print(f"Текущее время UTC: {datetime.utcnow()}")
            
            # Проверяем, есть ли записи за последние несколько часов
            hours_checks = [1, 3, 6, 12, 24]
            for hours in hours_checks:
                check_start = datetime.utcnow() - timedelta(hours=hours)
                count = SensorReading.query.filter_by(sensor_id=sensor_id)\
                    .filter(SensorReading.timestamp >= check_start)\
                    .count()
                print(f"Записей за последние {hours} часов: {count}")
        
        # Основной запрос
        readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
            .filter(SensorReading.timestamp >= start_time)\
            .filter(SensorReading.timestamp <= end_time)\
            .order_by(SensorReading.timestamp).all()
        
        print(f"Найдено записей в заданном периоде: {len(readings)}")
        
        # Если мало данных, попробуем расширить поиск
        if len(readings) < 5:
            print("Мало данных, расширяем поиск...")
            
            # Попробуем последние 24 часа
            extended_start = datetime.utcnow() - timedelta(hours=24)
            extended_readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
                .filter(SensorReading.timestamp >= extended_start)\
                .order_by(SensorReading.timestamp).all()
            
            print(f"За последние 24 часа найдено: {len(extended_readings)}")
            
            # Если и за 24 часа мало, берем просто последние записи
            if len(extended_readings) < 5:
                latest_readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
                    .order_by(SensorReading.timestamp.desc())\
                    .limit(20).all()
                
                # Сортируем по возрастанию времени
                latest_readings.reverse()
                print(f"Взяли последние 20 записей: {len(latest_readings)}")
                return latest_readings
            else:
                return extended_readings
        
        print(f"=== КОНЕЦ ОТЛАДКИ ===")
        return readings
    
    @staticmethod
    def get_readings_for_period_flexible(sensor_id, hours_back=1, min_points=10):
        """
        Гибкий метод получения данных - расширяет период до получения достаточного количества точек
        """
        print(f"=== Гибкий поиск данных для датчика {sensor_id} ===")
        
        periods_to_try = [hours_back, hours_back * 2, hours_back * 6, hours_back * 24, hours_back * 168]  # до недели
        
        for period in periods_to_try:
            start_time = datetime.utcnow() - timedelta(hours=period)
            readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
                .filter(SensorReading.timestamp >= start_time)\
                .order_by(SensorReading.timestamp).all()
            
            print(f"За последние {period} часов найдено: {len(readings)} записей")
            
            if len(readings) >= min_points:
                print(f"Достаточно данных найдено за {period} часов")
                return readings
        
        # Если ничего не нашли, берем последние записи
        print("Берем последние доступные записи...")
        latest_readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorReading.timestamp.desc())\
            .limit(50).all()
        
        latest_readings.reverse()  # Сортируем по возрастанию времени
        print(f"Получили последние {len(latest_readings)} записей")
        return latest_readings
    
    @staticmethod
    def add_sensor_reading(sensor_id, value, unit, timestamp=None):
        """Добавить новое показание датчика"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Проверяем наличие датчика
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ValueError(f"Датчик с ID {sensor_id} не найден")
        
        # Проверяем, не превышает ли значение пороги для тревоги
        is_alert = False
        alert_config = AlertConfig.query.filter_by(sensor_type=sensor.sensor_type).first()
        if alert_config:
            if alert_config.min_threshold is not None and value < alert_config.min_threshold:
                is_alert = True
            if alert_config.max_threshold is not None and value > alert_config.max_threshold:
                is_alert = True
        
        # Создаем новое показание
        reading = SensorReading(
            sensor_id=sensor_id,
            timestamp=timestamp,
            value=value,
            unit=unit,
            is_alert=is_alert
        )
        
        # Сохраняем в БД
        db.session.add(reading)
        db.session.commit()
        
        return reading
    
    @staticmethod
    def get_alerts(hours_back=24):
        """Получить все тревоги за последние N часов"""
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        return SensorReading.query.filter_by(is_alert=True)\
            .filter(SensorReading.timestamp >= start_time)\
            .order_by(SensorReading.timestamp.desc()).all()
    
    @staticmethod
    def debug_sensor_data(sensor_id):
        """Отладочный метод для анализа данных датчика"""
        print(f"\n=== ПОЛНАЯ ОТЛАДКА ДАТЧИКА {sensor_id} ===")
        
        # Общая статистика
        total_count = SensorReading.query.filter_by(sensor_id=sensor_id).count()
        print(f"Общее количество записей: {total_count}")
        
        if total_count == 0:
            print("Нет данных для этого датчика!")
            return
        
        # Последние записи
        latest = SensorReading.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorReading.timestamp.desc())\
            .limit(5).all()
        
        print(f"\nПоследние 5 записей:")
        for i, reading in enumerate(latest):
            print(f"  {i+1}. {reading.timestamp} -> {reading.value}")
        
        # Проверка временных зон
        if latest:
            latest_time = latest[0].timestamp
            current_utc = datetime.utcnow()
            time_diff = current_utc - latest_time
            
            print(f"\nАнализ времени:")
            print(f"Последняя запись: {latest_time}")
            print(f"Текущее UTC время: {current_utc}")
            print(f"Разница: {time_diff}")
            print(f"Часов назад: {time_diff.total_seconds() / 3600:.2f}")
        
        # Распределение по часам
        print(f"\nРаспределение записей по последним часам:")
        for hours in [1, 2, 6, 12, 24, 48, 168]:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            count = SensorReading.query.filter_by(sensor_id=sensor_id)\
                .filter(SensorReading.timestamp >= start_time)\
                .count()
            print(f"  За последние {hours} часов: {count} записей")
        
        print(f"=== КОНЕЦ ОТЛАДКИ ===\n")