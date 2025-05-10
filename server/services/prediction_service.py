# server/services/prediction_service.py

import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from server.services.data_service import DataService
from server.models.sensor_data import AlertConfig

class PredictionService:
    """Сервис для предсказания будущих показаний датчиков"""
    
    @staticmethod
    def predict_next_hours(sensor_id, hours_to_predict=24, history_hours=72):
        """
        Предсказать показания на следующие N часов
        
        Args:
            sensor_id: ID датчика
            hours_to_predict: на сколько часов вперед предсказывать
            history_hours: сколько часов исторических данных использовать
            
        Returns:
            список кортежей (время, значение)
        """
        # Получаем исторические данные
        start_time = datetime.utcnow() - timedelta(hours=history_hours)
        readings = DataService.get_readings_for_period(sensor_id, start_time)
        
        if len(readings) < 5:  # Нужно минимум 5 точек для построения модели
            return []
        
        # Подготавливаем данные
        X = []  # Временные метки (в часах от начала)
        y = []  # Значения
        
        start_timestamp = readings[0].timestamp.timestamp()
        for reading in readings:
            # Преобразуем время в часы с начала периода
            hours_since_start = (reading.timestamp.timestamp() - start_timestamp) / 3600
            X.append([hours_since_start])
            y.append(reading.value)
        
        # Обучаем модель
        model = LinearRegression()
        model.fit(X, y)
        
        # Готовим предсказания
        current_time = datetime.utcnow()  # Используем utcnow() вместо now(timezone.utc)
        predictions = []
        
        for hour in range(1, hours_to_predict + 1):
            prediction_time = current_time + timedelta(hours=hour)
            hours_since_start = (prediction_time.timestamp() - start_timestamp) / 3600
            
            # Предсказываем значение
            predicted_value = model.predict([[hours_since_start]])[0]
            
            predictions.append((prediction_time, predicted_value))
        
        return predictions
    
    @staticmethod
    def predict_alert_in_future(sensor_id, hours_ahead=24):
        """
        Проверить, будет ли тревога в ближайшие часы
        
        Returns:
            (bool, datetime) - будет ли тревога и когда
        """
        # Получаем настройки тревоги для датчика
        sensor = DataService.get_sensor(sensor_id)
        if not sensor:
            return False, None
        
        alert_config = AlertConfig.query.filter_by(sensor_type=sensor.sensor_type).first()
        if not alert_config or (alert_config.min_threshold is None and alert_config.max_threshold is None):
            return False, None
        
        # Получаем предсказания
        predictions = PredictionService.predict_next_hours(sensor_id, hours_ahead)
        
        # Проверяем, есть ли среди предсказаний значения, превышающие пороги
        for time, value in predictions:
            is_alert = False
            
            if alert_config.min_threshold is not None and value < alert_config.min_threshold:
                is_alert = True
            if alert_config.max_threshold is not None and value > alert_config.max_threshold:
                is_alert = True
                
            if is_alert:
                return True, time
                
        return False, None