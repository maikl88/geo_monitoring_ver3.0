# server/services/data_service.py (УПРОЩЕННАЯ ВЕРСИЯ)

from datetime import datetime, timedelta
from server.database.db import db
from server.models.sensor_data import Sensor, SensorReading, Building, AlertConfig

class DataService:
    """Упрощенный сервис данных"""
    
    @staticmethod
    def get_all_buildings():
        return Building.query.all()
    
    @staticmethod
    def get_building(building_id):
        return Building.query.get(building_id)
    
    @staticmethod
    def get_sensors_for_building(building_id):
        return Sensor.query.filter_by(building_id=building_id).all()
    
    @staticmethod
    def get_sensor(sensor_id):
        return Sensor.query.get(sensor_id)
    
    @staticmethod
    def get_latest_readings(sensor_id, limit=1):
        return SensorReading.query.filter_by(sensor_id=sensor_id)\
            .order_by(SensorReading.timestamp.desc())\
            .limit(limit).all()
    
    @staticmethod
    def get_readings_simple(sensor_id, hours_back=24):
        """Простое получение данных за период"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Сначала пробуем за запрошенный период
        readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
            .filter(SensorReading.timestamp >= start_time)\
            .filter(SensorReading.timestamp <= end_time)\
            .order_by(SensorReading.timestamp).all()
        
        # Если мало данных, расширяем поиск
        if len(readings) < 5:
            # Берем последние 100 записей
            readings = SensorReading.query.filter_by(sensor_id=sensor_id)\
                .order_by(SensorReading.timestamp.desc())\
                .limit(100).all()
            # Сортируем по возрастанию
            readings.reverse()
        
        return readings
    
    @staticmethod
    def add_sensor_reading(sensor_id, value, unit, timestamp=None):
        """Добавить показание датчика"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ValueError(f"Датчик {sensor_id} не найден")
        
        # Проверяем тревогу
        is_alert = False
        alert_config = AlertConfig.query.filter_by(sensor_type=sensor.sensor_type).first()
        if alert_config:
            if alert_config.min_threshold and value < alert_config.min_threshold:
                is_alert = True
            if alert_config.max_threshold and value > alert_config.max_threshold:
                is_alert = True
        
        reading = SensorReading(
            sensor_id=sensor_id,
            timestamp=timestamp,
            value=value,
            unit=unit,
            is_alert=is_alert
        )
        
        db.session.add(reading)
        db.session.commit()
        return reading
    
    @staticmethod
    def get_alerts(hours_back=24):
        """Получить тревоги"""
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        return SensorReading.query.filter_by(is_alert=True)\
            .filter(SensorReading.timestamp >= start_time)\
            .order_by(SensorReading.timestamp.desc()).all()