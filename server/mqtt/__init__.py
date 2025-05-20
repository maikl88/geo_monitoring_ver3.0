# server/mqtt/__init__.py

from flask import Flask
from .mqtt_client import MQTTClient

# Глобальная переменная для хранения экземпляра MQTT-клиента
mqtt_client = None

def init_mqtt(app=None):
    """
    Инициализирует MQTT-клиент и подключается к брокеру
    
    Args:
        app (Flask): Приложение Flask (опционально)
    """
    global mqtt_client
    
    # Создаем экземпляр MQTT-клиента, передавая приложение
    mqtt_client = MQTTClient(app=app)
    
    # Подключаемся к MQTT-брокеру
    success = mqtt_client.connect()
    
    if success and app:
        # Регистрируем обработчик для отключения при завершении работы приложения
        @app.teardown_appcontext
        def shutdown_mqtt(exception=None):
            mqtt_client.disconnect()
    
    return success