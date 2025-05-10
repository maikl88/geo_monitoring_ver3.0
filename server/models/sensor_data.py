# server/models/sensor_data.py

from datetime import datetime
from server.database.db import db

class Building(db.Model):
    """Модель для хранения информации о зданиях"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    floors = db.Column(db.Integer, nullable=True)
    construction_year = db.Column(db.Integer, nullable=True)
    building_type = db.Column(db.String(100), nullable=True)  # жилое, коммерческое, промышленное
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношение к датчикам определяем без указания primaryjoin
    sensors = db.relationship('Sensor', backref='building', lazy=True)
    
    def __repr__(self):
        return f'<Building {self.name}>'

class Sensor(db.Model):
    """Модель для хранения информации о датчиках"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)  # инклинометр, тензометр и т.д.
    location = db.Column(db.String(200), nullable=False)    # расположение в здании
    # Правильное определение внешнего ключа - это ключевой момент исправления
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    floor = db.Column(db.Integer, nullable=True)            # этаж (может быть null для внешних датчиков)
    position_x = db.Column(db.Float, nullable=True)         # координата X на схеме здания
    position_y = db.Column(db.Float, nullable=True)         # координата Y на схеме здания
    status = db.Column(db.String(20), default='active')     # активен, неактивен, требует обслуживания
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sensor {self.name} ({self.sensor_type})>'

class SensorReading(db.Model):
    """Модель для хранения показаний датчиков"""
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)             # числовое значение показания
    unit = db.Column(db.String(20), nullable=False)         # единица измерения (мм, градусы и т.д.)
    is_alert = db.Column(db.Boolean, default=False)         # флаг тревоги, если значение превышает норму
    
    # Отношение к датчику (позволяет легко получить данные о датчике)
    sensor = db.relationship('Sensor', backref=db.backref('readings', lazy=True))
    
    def __repr__(self):
        return f'<Reading for Sensor #{self.sensor_id}: {self.value} {self.unit}>'

class AlertConfig(db.Model):
    """Модель для хранения настроек срабатывания тревоги для конкретного типа датчика"""
    id = db.Column(db.Integer, primary_key=True)
    sensor_type = db.Column(db.String(50), nullable=False)
    min_threshold = db.Column(db.Float, nullable=True)  # минимальный порог (может быть null)
    max_threshold = db.Column(db.Float, nullable=True)  # максимальный порог (может быть null)
    unit = db.Column(db.String(20), nullable=False)     # единица измерения
    
    def __repr__(self):
        return f'<AlertConfig for {self.sensor_type}>'