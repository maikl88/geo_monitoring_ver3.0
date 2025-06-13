# server/services/approximation_service.py (УПРОЩЕННАЯ ВЕРСИЯ)

import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from server.services.data_service import DataService

class ApproximationService:
    """Упрощенный сервис аппроксимации"""
    
    @staticmethod
    def get_polynomial_approximation(sensor_id, hours_back=24, degree=3, num_points=50):
        """Простая полиномиальная аппроксимация"""
        
        # Получаем данные
        readings = DataService.get_readings_simple(sensor_id, hours_back)
        
        if len(readings) < 3:
            return {
                'original_data': [],
                'approximation': [],
                'error': f'Нужно минимум 3 точки данных, найдено: {len(readings)}'
            }
        
        # Конвертируем в простые списки
        timestamps = []
        values = []
        
        # Сортируем по времени
        readings.sort(key=lambda x: x.timestamp)
        
        # Базовое время для расчетов
        base_time = readings[0].timestamp
        
        for reading in readings:
            # Время в минутах от начала
            minutes = (reading.timestamp - base_time).total_seconds() / 60
            timestamps.append(minutes)
            values.append(reading.value)
        
        timestamps = np.array(timestamps)
        values = np.array(values)
        
        # Ограничиваем степень полинома
        max_degree = min(degree, len(readings) - 1, 4)
        
        try:
            # Создаем полиномиальную модель
            poly_features = PolynomialFeatures(degree=max_degree)
            poly_reg = LinearRegression()
            
            X = timestamps.reshape(-1, 1)
            X_poly = poly_features.fit_transform(X)
            poly_reg.fit(X_poly, values)
            
            # Создаем гладкую кривую
            smooth_timestamps = np.linspace(timestamps.min(), timestamps.max(), num_points)
            X_smooth = smooth_timestamps.reshape(-1, 1)
            X_smooth_poly = poly_features.transform(X_smooth)
            smooth_values = poly_reg.predict(X_smooth_poly)
            
            # Качество аппроксимации
            quality_score = poly_reg.score(X_poly, values)
            
            # Формируем данные для фронтенда
            original_data = []
            for reading in readings:
                original_data.append({
                    'timestamp': reading.timestamp.isoformat() + 'Z',  # Единый формат ISO
                    'value': reading.value
                })
            
            approximation_data = []
            for i, minutes in enumerate(smooth_timestamps):
                dt = base_time + timedelta(minutes=minutes)
                approximation_data.append({
                    'timestamp': dt.isoformat() + 'Z',  # Единый формат ISO
                    'value': float(smooth_values[i])
                })
            
            return {
                'original_data': original_data,
                'approximation': approximation_data,
                'quality_metrics': {
                    'method': 'polynomial',
                    'degree': max_degree,
                    'r_squared': quality_score,
                    'num_original_points': len(readings),
                    'num_approximation_points': num_points,
                    'requested_hours': hours_back
                },
                'error': None
            }
            
        except Exception as e:
            return {
                'original_data': [],
                'approximation': [],
                'error': f'Ошибка аппроксимации: {str(e)}'
            }
    
    @staticmethod
    def get_trend_analysis(sensor_id, hours_back=24):
        """Простой анализ тренда"""
        
        approximation_data = ApproximationService.get_polynomial_approximation(
            sensor_id, hours_back, 3, 20
        )
        
        if approximation_data['error'] or len(approximation_data['approximation']) < 2:
            return {
                'trend': 'unknown',
                'description': 'Недостаточно данных',
                'change_percent': 0,
                'start_value': None,
                'end_value': None
            }
        
        # Сравниваем начало и конец
        points = approximation_data['approximation']
        start_value = points[0]['value']
        end_value = points[-1]['value']
        
        # Вычисляем изменение в процентах
        if start_value != 0:
            change_percent = ((end_value - start_value) / abs(start_value)) * 100
        else:
            change_percent = 0
        
        # Определяем тренд
        if abs(change_percent) < 2:
            trend = 'stable'
            description = f'Стабильные показания (изменение {change_percent:+.1f}%)'
        elif change_percent > 10:
            trend = 'strongly_increasing'
            description = f'Сильный рост показаний (+{change_percent:.1f}%)'
        elif change_percent > 2:
            trend = 'increasing'
            description = f'Рост показаний (+{change_percent:.1f}%)'
        elif change_percent < -10:
            trend = 'strongly_decreasing'
            description = f'Сильное снижение показаний ({change_percent:.1f}%)'
        else:
            trend = 'decreasing'
            description = f'Снижение показаний ({change_percent:.1f}%)'
        
        return {
            'trend': trend,
            'description': description,
            'change_percent': change_percent,
            'start_value': start_value,
            'end_value': end_value
        }