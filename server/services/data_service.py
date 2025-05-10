# server/services/data_service.py

from datetime import datetime, timedelta
from server.database.db import db
from server.models.sensor_data import Sensor, SensorReading, Building, AlertConfig

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
        """Получить показания датчика за определенный период"""
        if end_time is None:
            end_time = datetime.utcnow()
            
        return SensorReading.query.filter_by(sensor_id=sensor_id)\
            .filter(SensorReading.timestamp >= start_time)\
            .filter(SensorReading.timestamp <= end_time)\
            .order_by(SensorReading.timestamp).all()
    
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