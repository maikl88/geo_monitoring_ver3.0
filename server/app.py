# server/app.py (УПРОЩЕННАЯ ВЕРСИЯ)

from flask import Flask, jsonify
from flask_cors import CORS
from server.database.db import init_db, db
from server.api.routes import api
from server.api.sensor_routes import sensor_api
from server.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, API_PREFIX
from server.utils.data_generator import DataGenerator
from server.models.sensor_data import Building, Sensor
from server.mqtt import init_mqtt

def create_app():
    app = Flask(__name__)
    
    # CORS для React
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Настройки
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация БД
    init_db(app)
    
    # Инициализация MQTT
    mqtt_success = init_mqtt(app)
    if not mqtt_success:
        app.logger.warning("MQTT не подключен")
    
    # Регистрация маршрутов
    app.register_blueprint(api, url_prefix=API_PREFIX)
    app.register_blueprint(sensor_api, url_prefix=f"{API_PREFIX}/geo")
    
    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Не найдено'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Ошибка сервера'}), 500
    
    # Инициализация тестовых данных
    @app.route('/init-sample-data')
    def init_sample_data():
        try:
            # Проверяем, есть ли уже данные
            if Building.query.first() is not None:
                return jsonify({'message': 'Данные уже есть'}), 200
            
            # Создаем здания
            buildings = DataGenerator.generate_sample_buildings(count=3)  # Уменьшено до 3
            db.session.add_all(buildings)
            db.session.commit()
            
            # Создаем настройки тревог
            alert_configs = DataGenerator.generate_alert_configs()
            db.session.add_all(alert_configs)
            db.session.commit()
            
            # Создаем датчики
            sensors = DataGenerator.generate_sample_sensors(buildings, count_per_building=3)
            db.session.add_all(sensors)
            db.session.commit()
            
            # Генерируем данные БЕЗ разрыва до текущего времени
            for sensor in Sensor.query.all():
                DataGenerator.generate_readings_for_sensor(
                    sensor, 
                    days_back=2,  # Только 2 дня для быстроты
                    readings_per_day=12  # Каждые 2 часа
                )
            
            return jsonify({
                'message': 'Тестовые данные созданы БЕЗ временного разрыва',
                'buildings': len(buildings),
                'sensors': len(sensors),
                'period': '2 дня данных до текущего момента'
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)