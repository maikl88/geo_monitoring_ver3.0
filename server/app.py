# server/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from server.database.db import init_db
from server.api.routes import api
from server.api.sensor_routes import sensor_api
from server.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, API_PREFIX, MQTT_BROKER_HOST, MQTT_BROKER_PORT
from server.utils.data_generator import DataGenerator
from server.database.db import db
from server.models.sensor_data import Building, Sensor
from server.mqtt import init_mqtt  # Импортируем функцию инициализации MQTT

def create_app():
    app = Flask(__name__)
    
    # Настройка CORS для работы с React-клиентом
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Настройка приложения
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация базы данных
    init_db(app)
    
    # Инициализация MQTT-клиента
    mqtt_success = init_mqtt(app)
    if not mqtt_success:
        app.logger.warning("Не удалось инициализировать MQTT-клиент. Данные с датчиков будут недоступны.")
    
    # Регистрация Blueprint'ов
    app.register_blueprint(api, url_prefix=API_PREFIX)
    app.register_blueprint(sensor_api, url_prefix=f"{API_PREFIX}/geo")
    
    # Обработка ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ресурс не найден'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
    
    # Маршрут для заполнения тестовыми данными
    @app.route('/init-sample-data')
    def init_sample_data():
        try:
            # Проверяем, есть ли уже данные
            if Building.query.first() is not None:
                return jsonify({'message': 'Данные уже существуют в БД'}), 200
            
            # Создаем тестовые здания
            buildings = DataGenerator.generate_sample_buildings(count=2)
            db.session.add_all(buildings)
            db.session.commit()
            
            # Создаем настройки тревог
            alert_configs = DataGenerator.generate_alert_configs()
            db.session.add_all(alert_configs)
            db.session.commit()
            
            # Создаем датчики
            sensors = DataGenerator.generate_sample_sensors(buildings, count_per_building=5)
            db.session.add_all(sensors)
            db.session.commit()
            
            # Генерация ИСТОРИЧЕСКИХ показаний для каждого датчика
            for sensor in Sensor.query.all():
                DataGenerator.generate_readings_for_sensor(sensor, days_back=7, readings_per_day=24)
            
            # Показания датчиков теперь будут приходить через MQTT
            return jsonify({
                'message': 'Тестовые данные созданы. Здания и датчики инициализированы.',
                'info': 'Для получения показаний запустите скрипт sensors_simulator.py',
                'buildings': len(buildings),
                'sensors': len(sensors)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)