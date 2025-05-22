# server/services/approximation_service.py (исправленная версия)

import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from server.services.data_service import DataService

class ApproximationService:
    """Сервис для создания полиномиальной аппроксимации данных датчиков"""
    
    @staticmethod
    def get_polynomial_approximation(sensor_id, hours_back=24, degree=3, num_points=100):
        """
        Создает полиномиальную аппроксимацию для показаний датчика
        
        Args:
            sensor_id: ID датчика
            hours_back: количество часов назад для анализа данных
            degree: степень полинома (2-5, рекомендуется 3-4)
            num_points: количество точек для гладкой кривой
            
        Returns:
            dict: содержит исходные данные и точки аппроксимации
        """
        # Получаем исторические данные
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        readings = DataService.get_readings_for_period(sensor_id, start_time)
        
        print(f"Найдено {len(readings)} показаний для датчика {sensor_id} за последние {hours_back} часов")
        
        # СНИЖАЕМ минимальное требование к количеству точек
        min_points = max(3, degree + 1)  # Минимум 3 точки или degree+1
        
        if len(readings) < min_points:
            return {
                'original_data': [],
                'approximation': [],
                'error': f'Недостаточно данных для аппроксимации. Найдено {len(readings)} точек, требуется минимум {min_points}'
            }
        
        # Подготавливаем данные
        timestamps = []
        values = []
        
        # Используем более точный способ расчета времени
        base_time = readings[0].timestamp
        for reading in readings:
            # Время в часах от первого показания
            time_diff = (reading.timestamp - base_time).total_seconds() / 3600
            timestamps.append(time_diff)
            values.append(reading.value)
        
        timestamps = np.array(timestamps)
        values = np.array(values)
        
        print(f"Временной диапазон: {timestamps.min():.2f} - {timestamps.max():.2f} часов")
        print(f"Значения: {values.min():.2f} - {values.max():.2f}")
        
        # АВТОМАТИЧЕСКИ адаптируем степень полинома к количеству данных
        max_degree = min(degree, len(readings) - 2)  # Максимум n-2 степень для n точек
        if max_degree < 2:
            max_degree = 2
        
        # Создаем полиномиальную модель
        try:
            # Используем Pipeline для удобства
            poly_model = Pipeline([
                ('poly', PolynomialFeatures(degree=max_degree, include_bias=True)),
                ('linear', LinearRegression())
            ])
            
            # Обучаем модель
            X = timestamps.reshape(-1, 1)
            poly_model.fit(X, values)
            
            # Создаем гладкую кривую - покрываем ВЕСЬ временной диапазон
            min_time = timestamps.min()
            max_time = timestamps.max()
            
            # Если данные за очень короткий период, расширяем диапазон
            if max_time - min_time < 0.1:  # Менее 6 минут
                time_range = max(0.5, max_time - min_time)  # Минимум 30 минут
                center_time = (min_time + max_time) / 2
                min_time = center_time - time_range / 2
                max_time = center_time + time_range / 2
            
            smooth_timestamps = np.linspace(min_time, max_time, num_points)
            smooth_values = poly_model.predict(smooth_timestamps.reshape(-1, 1))
            
            # Преобразуем обратно в datetime для фронтенда
            smooth_datetimes = []
            for t in smooth_timestamps:
                dt = base_time + timedelta(hours=float(t))
                smooth_datetimes.append(dt.isoformat())
            
            # Формируем исходные данные для фронтенда
            original_data = []
            for reading in readings:
                original_data.append({
                    'timestamp': reading.timestamp.isoformat(),
                    'value': reading.value
                })
            
            # Формируем данные аппроксимации
            approximation_data = []
            for i, dt in enumerate(smooth_datetimes):
                approximation_data.append({
                    'timestamp': dt,
                    'value': float(smooth_values[i])
                })
            
            # Вычисляем метрики качества аппроксимации
            predicted_original = poly_model.predict(X)
            mse = np.mean((values - predicted_original) ** 2)
            r_squared = poly_model.score(X, values)
            
            print(f"Аппроксимация успешна: степень={max_degree}, R²={r_squared:.3f}, точек={len(approximation_data)}")
            
            return {
                'original_data': original_data,
                'approximation': approximation_data,
                'quality_metrics': {
                    'mse': float(mse),
                    'r_squared': float(r_squared),
                    'degree': max_degree,
                    'num_original_points': len(readings),
                    'num_approximation_points': num_points,
                    'time_range_hours': float(max_time - min_time)
                },
                'error': None
            }
            
        except Exception as e:
            print(f"Ошибка при создании аппроксимации: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'original_data': [],
                'approximation': [],
                'error': f'Ошибка при создании аппроксимации: {str(e)}'
            }
    
    @staticmethod
    def get_trend_analysis(sensor_id, hours_back=24, degree=3):
        """
        Анализирует тренд на основе полиномиальной аппроксимации
        
        Returns:
            dict: анализ тренда (возрастающий, убывающий, стабильный)
        """
        approximation_data = ApproximationService.get_polynomial_approximation(
            sensor_id, hours_back, degree, 20  # Меньше точек для анализа тренда
        )
        
        if approximation_data['error'] or len(approximation_data['approximation']) < 2:
            return {
                'trend': 'unknown',
                'trend_strength': 0,
                'description': 'Недостаточно данных для анализа тренда'
            }
        
        # Анализируем изменение значений
        values = [point['value'] for point in approximation_data['approximation']]
        
        # Сравниваем начало и конец периода - БЕРЕМ БОЛЬШЕ ТОЧЕК для стабильности
        num_compare_points = min(3, len(values) // 4)  # Берем первые/последние 25% точек
        if num_compare_points < 1:
            num_compare_points = 1
            
        start_values = np.mean(values[:num_compare_points])
        end_values = np.mean(values[-num_compare_points:])
        
        change = end_values - start_values
        change_percent = (change / abs(start_values)) * 100 if start_values != 0 else 0
        
        # БОЛЕЕ ГИБКИЕ пороги для определения тренда
        threshold_small = 2   # 2% для малых изменений
        threshold_large = 15  # 15% для больших изменений
        
        # Определяем тренд
        if abs(change_percent) < threshold_small:
            trend = 'stable'
            description = f'Показания стабильны (изменение {change_percent:+.1f}%)'
        elif change_percent > threshold_large:
            trend = 'strongly_increasing'
            description = f'Сильный рост показаний (+{change_percent:.1f}%)'
        elif change_percent > threshold_small:
            trend = 'increasing'
            description = f'Рост показаний (+{change_percent:.1f}%)'
        elif change_percent < -threshold_large:
            trend = 'strongly_decreasing'
            description = f'Сильное снижение показаний ({change_percent:.1f}%)'
        else:  # change_percent < -threshold_small
            trend = 'decreasing'
            description = f'Снижение показаний ({change_percent:.1f}%)'
        
        return {
            'trend': trend,
            'trend_strength': abs(change_percent),
            'change_percent': change_percent,
            'description': description,
            'start_value': start_values,
            'end_value': end_values
        }
    
    @staticmethod
    def get_optimal_degree(sensor_id, hours_back=24, max_degree=5):
        """
        Определяет оптимальную степень полинома для аппроксимации
        
        Returns:
            int: оптимальная степень полинома
        """
        # Получаем данные
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        readings = DataService.get_readings_for_period(sensor_id, start_time)
        
        if len(readings) < 6:  # Снижаем требование
            return 2  # Минимальная степень для малого количества данных
        
        # Подготавливаем данные
        timestamps = []
        values = []
        
        base_time = readings[0].timestamp
        for reading in readings:
            time_diff = (reading.timestamp - base_time).total_seconds() / 3600
            timestamps.append(time_diff)
            values.append(reading.value)
        
        timestamps = np.array(timestamps).reshape(-1, 1)
        values = np.array(values)
        
        best_degree = 2
        best_score = -float('inf')
        
        # Ограничиваем максимальную степень количеством данных
        max_allowed_degree = min(max_degree, len(readings) // 2)
        
        # Тестируем разные степени полинома
        for degree in range(2, max_allowed_degree + 1):
            try:
                poly_model = Pipeline([
                    ('poly', PolynomialFeatures(degree=degree)),
                    ('linear', LinearRegression())
                ])
                
                poly_model.fit(timestamps, values)
                score = poly_model.score(timestamps, values)
                
                # Штрафуем за переобучение (слишком высокие степени)
                penalty = (degree - 2) * 0.03  # 3% штрафа за каждую степень выше 2
                adjusted_score = score - penalty
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_degree = degree
                    
            except:
                continue
        
        print(f"Оптимальная степень полинома: {best_degree} (из {len(readings)} точек)")
        return best_degree