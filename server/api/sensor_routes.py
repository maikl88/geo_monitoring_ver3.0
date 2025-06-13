# server/api/sensor_routes.py (УПРОЩЕННАЯ ВЕРСИЯ)

from flask import Blueprint, jsonify, request
from server.services.data_service import DataService
from server.services.approximation_service import ApproximationService
from server.models.sensor_data import Sensor, Building
from datetime import datetime, timedelta

sensor_api = Blueprint('sensor_api', __name__)

@sensor_api.route('/buildings', methods=['GET'])
def get_buildings():
    """Список всех зданий"""
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

@sensor_api.route('/buildings/<int:building_id>', methods=['GET'])
def get_building(building_id):
    """Информация о здании"""
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
        'building_type': building.building_type,
        'sensors': sensors_data
    }
    
    return jsonify(result), 200

@sensor_api.route('/sensors', methods=['GET'])
def get_sensors():
    """Список датчиков"""
    building_id = request.args.get('building_id')
    
    if building_id:
        sensors = DataService.get_sensors_for_building(int(building_id))
    else:
        sensors = Sensor.query.all()
    
    result = []
    for sensor in sensors:
        # Получаем последнее показание
        last_readings = DataService.get_latest_readings(sensor.id, 1)
        last_reading = None
        
        if last_readings:
            reading = last_readings[0]
            last_reading = {
                'value': reading.value,
                'unit': reading.unit,
                'timestamp': reading.timestamp.isoformat() + 'Z',
                'is_alert': reading.is_alert
            }
        
        result.append({
            'id': sensor.id,
            'name': sensor.name,
            'type': sensor.sensor_type,
            'building_id': sensor.building_id,
            'location': sensor.location,
            'floor': sensor.floor,
            'status': sensor.status,
            'last_reading': last_reading
        })
    
    return jsonify(result), 200

@sensor_api.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    """Информация о датчике"""
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    # Последнее показание
    last_readings = DataService.get_latest_readings(sensor_id, 1)
    last_reading = None
    
    if last_readings:
        reading = last_readings[0]
        last_reading = {
            'value': reading.value,
            'unit': reading.unit,
            'timestamp': reading.timestamp.isoformat() + 'Z',
            'is_alert': reading.is_alert
        }
    
    result = {
        'id': sensor.id,
        'name': sensor.name,
        'type': sensor.sensor_type,
        'building_id': sensor.building_id,
        'location': sensor.location,
        'floor': sensor.floor,
        'status': sensor.status,
        'last_reading': last_reading
    }
    
    return jsonify(result), 200

@sensor_api.route('/sensors/<int:sensor_id>/readings', methods=['GET'])
def get_sensor_readings(sensor_id):
    """Показания датчика"""
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    # Период из параметров (по умолчанию 24 часа)
    hours = request.args.get('hours', 24, type=int)
    
    # Получаем данные
    readings = DataService.get_readings_simple(sensor_id, hours)
    
    result = []
    for reading in readings:
        result.append({
            'id': reading.id,
            'value': reading.value,
            'unit': reading.unit,
            'timestamp': reading.timestamp.isoformat() + 'Z',  # Единый формат
            'is_alert': reading.is_alert
        })
    
    return jsonify(result), 200

@sensor_api.route('/sensors/<int:sensor_id>/approximation', methods=['GET'])
def get_sensor_approximation(sensor_id):
    """Аппроксимация для датчика"""
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    # Параметры
    hours_back = request.args.get('hours', 24, type=int)
    degree = request.args.get('degree', type=int)
    num_points = request.args.get('points', 50, type=int)
    
    # Ограничения
    hours_back = max(1, min(hours_back, 168))  # 1 час - 1 неделя
    num_points = max(10, min(num_points, 100))  # 10-100 точек
    
    if degree is None:
        degree = 3  # По умолчанию
    degree = max(2, min(degree, 5))  # 2-5 степень
    
    try:
        # Получаем аппроксимацию
        approximation_data = ApproximationService.get_polynomial_approximation(
            sensor_id, hours_back, degree, num_points
        )
        
        # Получаем анализ тренда
        trend_analysis = None
        if not approximation_data['error']:
            try:
                trend_analysis = ApproximationService.get_trend_analysis(sensor_id, hours_back)
            except Exception as e:
                print(f"Ошибка анализа тренда: {e}")
                trend_analysis = {
                    'trend': 'unknown',
                    'description': 'Ошибка анализа тренда'
                }
        
        return jsonify({
            'sensor_id': sensor_id,
            'approximation_data': approximation_data,
            'trend_analysis': trend_analysis,
            'parameters': {
                'hours_back': hours_back,
                'degree': degree,
                'num_points': num_points
            }
        }), 200
        
    except Exception as e:
        print(f"Ошибка аппроксимации: {e}")
        return jsonify({
            'sensor_id': sensor_id,
            'approximation_data': {
                'original_data': [],
                'approximation': [],
                'error': f'Ошибка сервера: {str(e)}'
            },
            'trend_analysis': {
                'trend': 'error',
                'description': f'Ошибка: {str(e)}'
            }
        }), 200

@sensor_api.route('/alerts', methods=['GET'])
def get_alerts():
    """Список тревог"""
    hours = request.args.get('hours', 24, type=int)
    alerts = DataService.get_alerts(hours_back=hours)
    
    result = []
    for alert in alerts:
        sensor = DataService.get_sensor(alert.sensor_id)
        
        result.append({
            'id': alert.id,
            'sensor_id': alert.sensor_id,
            'sensor_name': sensor.name if sensor else 'Неизвестный',
            'building_id': sensor.building_id if sensor else None,
            'value': alert.value,
            'unit': alert.unit,
            'timestamp': alert.timestamp.isoformat() + 'Z'
        })
    
    return jsonify(result), 200

@sensor_api.route('/sensors/<int:sensor_id>/readings', methods=['POST'])
def add_sensor_reading(sensor_id):
    """Добавить показание датчика"""
    sensor = DataService.get_sensor(sensor_id)
    
    if not sensor:
        return jsonify({'error': 'Датчик не найден'}), 404
    
    data = request.json
    if not data or 'value' not in data:
        return jsonify({'error': 'Нужно указать value'}), 400
    
    value = data.get('value')
    unit = data.get('unit', 'единицы')
    
    try:
        reading = DataService.add_sensor_reading(sensor_id, value, unit)
        
        result = {
            'id': reading.id,
            'sensor_id': reading.sensor_id,
            'value': reading.value,
            'unit': reading.unit,
            'timestamp': reading.timestamp.isoformat() + 'Z',
            'is_alert': reading.is_alert
        }
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500