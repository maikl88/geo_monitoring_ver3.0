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
    

# Полином 1-ой степени

# server/services/approximation_service.py (УЛУЧШЕННАЯ ВЕРСИЯ)

# import numpy as np
# from datetime import datetime, timedelta
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.linear_model import LinearRegression
# from scipy.interpolate import UnivariateSpline
# from server.services.data_service import DataService

# class ApproximationService:
#     """Улучшенный сервис аппроксимации с адаптивным выбором метода"""
    
#     @staticmethod
#     def analyze_data_characteristics(values):
#         """Анализирует характеристики данных для выбора метода"""
#         if len(values) < 3:
#             return {'type': 'insufficient', 'noise_level': 'unknown'}
        
#         # Вычисляем статистики
#         data_range = np.max(values) - np.min(values)
#         std_dev = np.std(values)
#         mean_val = np.mean(values)
        
#         # Определяем уровень шума
#         noise_ratio = std_dev / (abs(mean_val) + 1e-10)  # Избегаем деления на ноль
        
#         # Определяем характер изменений
#         linear_trend = np.polyfit(range(len(values)), values, 1)[0]
#         trend_strength = abs(linear_trend) * len(values) / (std_dev + 1e-10)
        
#         return {
#             'type': 'flat' if data_range < std_dev * 2 else 'varying',
#             'noise_level': 'high' if noise_ratio > 0.3 else 'medium' if noise_ratio > 0.1 else 'low',
#             'trend_strength': trend_strength,
#             'data_range': data_range,
#             'std_dev': std_dev,
#             'noise_ratio': noise_ratio
#         }
    
#     @staticmethod
#     def choose_optimal_method(values, characteristics):
#         """Выбирает оптимальный метод аппроксимации"""
        
#         # Для плоских данных с высоким шумом
#         if characteristics['type'] == 'flat' and characteristics['noise_level'] == 'high':
#             return {
#                 'method': 'moving_average',
#                 'degree': None,
#                 'window': max(3, len(values) // 10)
#             }
        
#         # Для данных с низким трендом
#         if characteristics['trend_strength'] < 0.5:
#             return {
#                 'method': 'linear',
#                 'degree': 1,
#                 'window': None
#             }
        
#         # Для данных с умеренным шумом
#         if characteristics['noise_level'] in ['low', 'medium']:
#             optimal_degree = min(3, len(values) // 4, 2)  # Ограничиваем степень
#             return {
#                 'method': 'polynomial',
#                 'degree': optimal_degree,
#                 'window': None
#             }
        
#         # Для очень зашумленных данных
#         return {
#             'method': 'spline_smooth',
#             'degree': None,
#             'smoothing': characteristics['noise_ratio'] * 10
#         }
    
#     @staticmethod
#     def apply_moving_average(values, window):
#         """Скользящее среднее для сильно зашумленных данных"""
#         if len(values) < window:
#             return values
        
#         # Простое скользящее среднее
#         smoothed = []
#         for i in range(len(values)):
#             start_idx = max(0, i - window // 2)
#             end_idx = min(len(values), i + window // 2 + 1)
#             smoothed.append(np.mean(values[start_idx:end_idx]))
        
#         return np.array(smoothed)
    
#     @staticmethod
#     def get_polynomial_approximation(sensor_id, hours_back=24, degree=None, num_points=50):
#         """Улучшенная полиномиальная аппроксимация с адаптивным выбором метода"""
        
#         # Получаем данные
#         readings = DataService.get_readings_simple(sensor_id, hours_back)
        
#         if len(readings) < 3:
#             return {
#                 'original_data': [],
#                 'approximation': [],
#                 'error': f'Недостаточно данных для аппроксимации. Найдено {len(readings)} точек, требуется минимум 3'
#             }
        
#         # Подготавливаем данные
#         timestamps = []
#         values = []
        
#         readings.sort(key=lambda x: x.timestamp)
#         base_time = readings[0].timestamp
        
#         for reading in readings:
#             minutes = (reading.timestamp - base_time).total_seconds() / 60
#             timestamps.append(minutes)
#             values.append(reading.value)
        
#         timestamps = np.array(timestamps)
#         values = np.array(values)
        
#         # Анализируем характеристики данных
#         characteristics = ApproximationService.analyze_data_characteristics(values)
#         method_config = ApproximationService.choose_optimal_method(values, characteristics)
        
#         print(f"Анализ данных: {characteristics}")
#         print(f"Выбранный метод: {method_config}")
        
#         # Подготавливаем исходные данные для фронтенда
#         original_data = []
#         for reading in readings:
#             original_data.append({
#                 'timestamp': reading.timestamp.isoformat() + 'Z',
#                 'value': reading.value
#             })
        
#         try:
#             # Применяем выбранный метод
#             method = method_config['method']
            
#             if method == 'moving_average':
#                 # Скользящее среднее
#                 smooth_values = ApproximationService.apply_moving_average(
#                     values, method_config['window']
#                 )
#                 smooth_timestamps = timestamps
#                 quality_score = 1 - characteristics['noise_ratio']  # Примерная оценка
#                 method_description = f"Скользящее среднее (окно {method_config['window']})"
                
#             elif method == 'linear':
#                 # Линейная регрессия
#                 linear_reg = LinearRegression()
#                 X = timestamps.reshape(-1, 1)
#                 linear_reg.fit(X, values)
                
#                 smooth_timestamps = np.linspace(timestamps.min(), timestamps.max(), num_points)
#                 smooth_values = linear_reg.predict(smooth_timestamps.reshape(-1, 1))
#                 quality_score = linear_reg.score(X, values)
#                 method_description = "Линейная регрессия"
                
#             elif method == 'spline_smooth':
#                 # Сглаживающий сплайн
#                 smoothing_factor = method_config.get('smoothing', 1.0)
#                 try:
#                     spline = UnivariateSpline(timestamps, values, s=smoothing_factor * len(values))
#                     smooth_timestamps = np.linspace(timestamps.min(), timestamps.max(), num_points)
#                     smooth_values = spline(smooth_timestamps)
                    
#                     # Оценка качества через остатки
#                     predicted_original = spline(timestamps)
#                     quality_score = 1 - np.mean((values - predicted_original) ** 2) / np.var(values)
#                     method_description = f"Сглаживающий сплайн (s={smoothing_factor:.1f})"
#                 except:
#                     # Fallback к линейной регрессии
#                     return ApproximationService.get_polynomial_approximation(
#                         sensor_id, hours_back, 1, num_points
#                     )
            
#             else:  # polynomial
#                 # Полиномиальная аппроксимация
#                 optimal_degree = method_config['degree'] or min(degree or 3, len(readings) - 1, 3)
                
#                 poly_features = PolynomialFeatures(degree=optimal_degree)
#                 poly_reg = LinearRegression()
                
#                 X = timestamps.reshape(-1, 1)
#                 X_poly = poly_features.fit_transform(X)
#                 poly_reg.fit(X_poly, values)
                
#                 smooth_timestamps = np.linspace(timestamps.min(), timestamps.max(), num_points)
#                 X_smooth = smooth_timestamps.reshape(-1, 1)
#                 X_smooth_poly = poly_features.transform(X_smooth)
#                 smooth_values = poly_reg.predict(X_smooth_poly)
                
#                 quality_score = poly_reg.score(X_poly, values)
#                 method_description = f"Полином {optimal_degree}-й степени"
            
#             # Формируем данные аппроксимации
#             approximation_data = []
#             for i, minutes in enumerate(smooth_timestamps):
#                 dt = base_time + timedelta(minutes=float(minutes))
#                 approximation_data.append({
#                     'timestamp': dt.isoformat() + 'Z',
#                     'value': float(smooth_values[i])
#                 })
            
#             # Улучшенная оценка качества
#             quality_assessment = "отличное" if quality_score > 0.9 else \
#                                "хорошее" if quality_score > 0.7 else \
#                                "удовлетворительное" if quality_score > 0.4 else \
#                                "плохое"
            
#             return {
#                 'original_data': original_data,
#                 'approximation': approximation_data,
#                 'quality_metrics': {
#                     'method': method,
#                     'degree': method_config.get('degree'),
#                     'r_squared': max(0, min(1, quality_score)),  # Ограничиваем 0-1
#                     'quality_assessment': quality_assessment,
#                     'num_original_points': len(readings),
#                     'num_approximation_points': len(approximation_data),
#                     'data_characteristics': characteristics,
#                     'method_description': method_description,
#                     'requested_hours': hours_back
#                 },
#                 'error': None
#             }
            
#         except Exception as e:
#             print(f"Ошибка при создании аппроксимации: {e}")
            
#             return {
#                 'original_data': original_data,
#                 'approximation': [],
#                 'error': f'Ошибка при создании аппроксимации: {str(e)}'
#             }
    
#     @staticmethod
#     def get_trend_analysis(sensor_id, hours_back=24):
#         """Улучшенный анализ тренда"""
        
#         approximation_data = ApproximationService.get_polynomial_approximation(
#             sensor_id, hours_back, None, 20
#         )
        
#         if approximation_data['error'] or len(approximation_data['approximation']) < 2:
#             return {
#                 'trend': 'unknown',
#                 'description': 'Недостаточно данных для анализа тренда',
#                 'change_percent': 0,
#                 'start_value': None,
#                 'end_value': None
#             }
        
#         # Анализируем изменение значений
#         points = approximation_data['approximation']
#         start_value = points[0]['value']
#         end_value = points[-1]['value']
        
#         # Вычисляем изменение в процентах
#         if abs(start_value) > 1e-10:
#             change_percent = ((end_value - start_value) / abs(start_value)) * 100
#         else:
#             change_percent = 0
        
#         # Определяем тренд с учетом характеристик данных
#         characteristics = approximation_data['quality_metrics'].get('data_characteristics', {})
#         noise_level = characteristics.get('noise_level', 'medium')
        
#         # Адаптивные пороги в зависимости от уровня шума
#         if noise_level == 'high':
#             small_threshold = 5.0   # Для зашумленных данных выше пороги
#             large_threshold = 15.0
#         else:
#             small_threshold = 2.0   # Для чистых данных ниже пороги
#             large_threshold = 10.0
        
#         # Определяем тренд
#         if abs(change_percent) < small_threshold:
#             trend = 'stable'
#             description = f'Стабильные показания (изменение {change_percent:+.1f}%)'
#         elif change_percent > large_threshold:
#             trend = 'strongly_increasing'
#             description = f'Сильный рост показаний (+{change_percent:.1f}%)'
#         elif change_percent > small_threshold:
#             trend = 'increasing'
#             description = f'Рост показаний (+{change_percent:.1f}%)'
#         elif change_percent < -large_threshold:
#             trend = 'strongly_decreasing'
#             description = f'Сильное снижение показаний ({change_percent:.1f}%)'
#         else:
#             trend = 'decreasing'
#             description = f'Снижение показаний ({change_percent:.1f}%)'
        
#         # Добавляем контекст о качестве данных
#         if noise_level == 'high':
#             description += f" (высокий уровень шумов)"
        
#         return {
#             'trend': trend,
#             'description': description,
#             'change_percent': change_percent,
#             'start_value': start_value,
#             'end_value': end_value,
#             'data_quality': approximation_data['quality_metrics']['quality_assessment'],
#             'noise_level': noise_level
#         }