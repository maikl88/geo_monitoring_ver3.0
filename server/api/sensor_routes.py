# server/api/sensor_routes.py

from flask import Blueprint, jsonify, request, current_app
from server.services.data_service import DataService
from server.services.prediction_service import PredictionService
from server.database.db import db
from server.models.sensor_data import Sensor, Building, SensorReading, AlertConfig
from datetime import datetime, timedelta


# Создаем Blueprint для маршрутов, связанных с датчиками
sensor_api = Blueprint('sensor_api', __name__)

# Получение списка всех зданий
@sensor_api.route('/buildings', methods=['GET'])
def get_buildings():
    buildings = DataService.get_all_buildings()
    result = []
    
    for building in buildings:
        result.append({
            'id': building.id,
            'name': building.name,
            'address': building.address,
            'floors': building.floors,
            'building_type': building.building_type
        })
    
    return jsonify(result), 200

# Получение информации о конкретном здании
@sensor_api.route('/buildings/<int:building_id>', methods=['GET'])
def get_building(building_id):
    building = DataService.get_building(building_id)
    
    if not building:
        return jsonify({'error': 'Здание не найдено'}), 404
    
    sensors = DataService.get_sensors_for_building(building_id)
    sensors_data = []
    
    for sensor in sensors:
        sensors_data.append({
            'id': sensor.id,
            'name': sensor.name,
            'type': sensor.sensor_type,
            'location': sensor.location,
            'floor': sensor.floor,
            'status': sensor.status
        })
    
    result = {
        'id': building.id,
        'name': building.name,
        'address': building.address,
        'floors': building.floors,
        'construction_year': building.construction_year,
        'building_type': building.building_type,
        'sensors': sensors_data
    }
    
    return jsonify(result), 200

# Получение списка всех датчиков
@sensor_api.route('/sensors', methods=['GET'])
def get_sensors():
    # Опциональный параметр building_id для фильтрации
    building_id = request.args.get('building_id')
    
    if building_id:
        sensors = DataService.get_sensors_for_building(int(building_id))
    else:
        sensors = Sensor.query.all()
    
    result = []
    
    for sensor in sensors:
        result.append({
            'id': sensor.id,
            'name': sensor.name,
            'type': sensor.sensor_type,
            'building_id': sensor.building_id,
            'location': sensor.location,
            'floor': sensor.floor,
            'status': sensor.status
        })
    
    return jsonify(result), 200

# Получение информации о конкретном датчике
@sensor_api.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    # Получаем последнее показание
    last_readings = DataService.get_latest_readings(sensor_id, limit=1)
    last_reading = None
    
    if last_readings:
        last_reading = {
            'value': last_readings[0].value,
            'unit': last_readings[0].unit,
            'timestamp': last_readings[0].timestamp.isoformat(),
            'is_alert': last_readings[0].is_alert
        }
    
    result = {
        'id': sensor.id,
        'name': sensor.name,
        'type': sensor.sensor_type,
        'building_id': sensor.building_id,
        'location': sensor.location,
        'floor': sensor.floor,
        'position_x': sensor.position_x,
        'position_y': sensor.position_y,
        'status': sensor.status,
        'last_reading': last_reading
    }
    
    return jsonify(result), 200

# Получение показаний датчика за период
@sensor_api.route('/sensors/<int:sensor_id>/readings', methods=['GET'])
def get_sensor_readings(sensor_id):
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    # Получаем период из query параметров (по умолчанию последние 24 часа)
    hours = request.args.get('hours', 24, type=int)
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    print(f"Запрос показаний датчика {sensor_id} за последние {hours} часов (с {start_time})")
    
    try:
        # Получаем ВСЕ показания для данного датчика из БД напрямую через SQLite
        import sqlite3
        import os
        from server.config import SQLITE_DB_PATH
        
        print(f"Используем прямой доступ к БД: {SQLITE_DB_PATH}")
        
        # Подключаемся к БД
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Чтобы получить доступ к колонкам по имени
        cursor = conn.cursor()
        
        # Общее количество показаний
        cursor.execute("SELECT COUNT(*) FROM sensor_reading WHERE sensor_id = ?", (sensor_id,))
        total_count = cursor.fetchone()[0]
        print(f"Всего найдено {total_count} показаний для датчика {sensor_id}")
        
        # Запрашиваем все показания для датчика
        cursor.execute("""
            SELECT id, sensor_id, timestamp, value, unit, is_alert
            FROM sensor_reading 
            WHERE sensor_id = ? 
            ORDER BY timestamp DESC
        """, (sensor_id,))
        
        readings = cursor.fetchall()
        print(f"Получено {len(readings)} показаний")
        
        # Формируем ответ
        result = []
        for row in readings:
            result.append({
                'id': row['id'],
                'value': row['value'],
                'unit': row['unit'],
                'timestamp': row['timestamp'],
                'is_alert': bool(row['is_alert'])
            })
        
        conn.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Ошибка при получении показаний: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Получение предсказаний для датчика
@sensor_api.route('/sensors/<int:sensor_id>/predictions', methods=['GET'])
def get_sensor_predictions(sensor_id):
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    # Получаем параметры прогнозирования
    hours_ahead = request.args.get('hours', 24, type=int)
    
    # Получаем предсказания
    predictions = PredictionService.predict_next_hours(sensor_id, hours_ahead)
    
    result = []
    for time, value in predictions:
        result.append({
            'timestamp': time.isoformat(),
            'value': value
        })
    
    # Проверяем, будет ли тревога в ближайшее время
    will_alert, alert_time = PredictionService.predict_alert_in_future(sensor_id, hours_ahead)
    
    return jsonify({
        'sensor_id': sensor_id,
        'predictions': result,
        'alert_prediction': {
            'will_alert': will_alert,
            'alert_time': alert_time.isoformat() if alert_time else None
        }
    }), 200

# Получение тревог системы
@sensor_api.route('/alerts', methods=['GET'])
def get_alerts():
    # Фильтр по времени
    hours = request.args.get('hours', 24, type=int)
    
    alerts = DataService.get_alerts(hours_back=hours)
    result = []
    
    for alert in alerts:
        sensor = DataService.get_sensor(alert.sensor_id)
        
        result.append({
            'id': alert.id,
            'sensor_id': alert.sensor_id,
            'sensor_name': sensor.name if sensor else 'Неизвестный датчик',
            'building_id': sensor.building_id if sensor else None,
            'value': alert.value,
            'unit': alert.unit,
            'timestamp': alert.timestamp.isoformat()
        })
    
    return jsonify(result), 200

# Добавление нового показания датчика
@sensor_api.route('/sensors/<int:sensor_id>/readings', methods=['POST'])
def add_sensor_reading(sensor_id):
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    data = request.json
    
    if not data or 'value' not in data:
        return jsonify({'error': 'Необходимо указать значение датчика (value)'}), 400
    
    # Получаем данные из запроса
    value = data.get('value')
    unit = data.get('unit')
    
    # Если единица измерения не указана, используем стандартную для типа датчика
    if not unit:
        alert_config = AlertConfig.query.filter_by(sensor_type=sensor.sensor_type).first()
        unit = alert_config.unit if alert_config else 'единицы'
    
    # Добавляем показание
    try:
        reading = DataService.add_sensor_reading(sensor_id, value, unit)
        
        result = {
            'id': reading.id,
            'sensor_id': reading.sensor_id,
            'value': reading.value,
            'unit': reading.unit,
            'timestamp': reading.timestamp.isoformat(),
            'is_alert': reading.is_alert
        }
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500