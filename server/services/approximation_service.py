# server/services/approximation_service.py (исправленная версия для гладкой кривой)

import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from scipy.interpolate import UnivariateSpline, interp1d
from server.services.data_service import DataService

class ApproximationService:
    """Сервис для создания полиномиальной аппроксимации данных датчиков"""
    
    @staticmethod
    def get_polynomial_approximation(sensor_id, hours_back=1, degree=2, num_points=50):
        """
        Создает гладкую полиномиальную аппроксимацию для показаний датчика
        
        Args:
            sensor_id: ID датчика
            hours_back: количество часов назад для анализа данных (по умолчанию 1)
            degree: степень полинома (2-5, рекомендуется 3)
            num_points: количество точек для гладкой кривой (увеличено до 50)
            
        Returns:
            dict: содержит исходные данные и точки аппроксимации
        """
        # Используем отладочный метод для понимания ситуации
        DataService.debug_sensor_data(sensor_id)
        
        # Получаем данные за запрошенный период
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        readings = DataService.get_readings_for_period(sensor_id, start_time)
        
        print(f"За период {hours_back}ч найдено {len(readings)} показаний")
        
        # Если данных мало для запрошенного периода, используем больше данных для обучения модели,
        # но аппроксимацию строим только в рамках запрошенного периода
        training_readings = readings
        if len(readings) < 5:
            print(f"Мало данных за {hours_back}ч, используем данные за больший период для обучения модели...")
            training_readings = DataService.get_readings_for_period_flexible(
                sensor_id, 
                hours_back=hours_back, 
                min_points=10
            )
            print(f"Для обучения модели используем {len(training_readings)} точек")
        
        # Проверяем минимальное количество данных
        if len(training_readings) < 3:
            return {
                'original_data': [],
                'approximation': [],
                'error': f'Недостаточно данных для аппроксимации. Найдено {len(training_readings)} точек, требуется минимум 3'
            }
            return {
                'original_data': [],
                'approximation': [],
                'error': f'Недостаточно данных для аппроксимации. Найдено {len(readings)} точек, требуется минимум 3'
            }
        
        # Подготавливаем данные для обучения модели
        timestamps = []
        values = []
        
        # Сортируем показания по времени
        training_readings = sorted(training_readings, key=lambda x: x.timestamp)
        
        # Используем время в минутах от первого показания для лучшей точности
        base_time = training_readings[0].timestamp
        for reading in training_readings:
            # Время в минутах от первого показания
            time_diff = (reading.timestamp - base_time).total_seconds() / 60
            timestamps.append(time_diff)
            values.append(reading.value)
        
        timestamps = np.array(timestamps)
        values = np.array(values)
        
        print(f"Данные для обучения: {timestamps.min():.1f} - {timestamps.max():.1f} минут")
        print(f"Значения: {values.min():.2f} - {values.max():.2f}")
        
        # Подготавливаем исходные данные только за запрошенный период для отображения
        original_data = []
        for reading in readings:  # Используем readings (за запрошенный период), а не training_readings
            original_data.append({
                'timestamp': reading.timestamp.isoformat(),
                'value': reading.value
            })
        
        # Автоматически выбираем лучший метод аппроксимации
        try:
            # Создаем гладкую кривую СТРОГО в рамках запрошенного периода
            # Определяем временные границы на основе запрошенного периода, а не данных
            current_time = datetime.utcnow()
            period_start = current_time - timedelta(hours=hours_back)
            
            # Время в минутах от базового времени
            min_time = (period_start - base_time).total_seconds() / 60
            max_time = (current_time - base_time).total_seconds() / 60
            
            print(f"Границы аппроксимации: {min_time:.1f} - {max_time:.1f} минут (период {hours_back}ч)")
            print(f"Границы данных: {timestamps.min():.1f} - {timestamps.max():.1f} минут")
            
            # Создаем равномерно распределенные точки времени для аппроксимации
            smooth_timestamps = np.linspace(min_time, max_time, num_points)
            
            # Определяем оптимальную степень полинома
            optimal_degree = min(degree, len(training_readings) - 1, 4)  # Максимум 4 степень
            
            # Метод 1: Попробуем полиномиальную аппроксимацию
            success_poly = False
            if len(training_readings) >= optimal_degree + 1:
                try:
                    poly_model = Pipeline([
                        ('poly', PolynomialFeatures(degree=optimal_degree, include_bias=True)),
                        ('linear', LinearRegression())
                    ])
                    
                    X = timestamps.reshape(-1, 1)
                    poly_model.fit(X, values)
                    
                    # Проверяем качество аппроксимации
                    r_squared = poly_model.score(X, values)
                    if r_squared > 0.3:  # Приемлемое качество
                        success_poly = True
                        chosen_method = "polynomial"
                        print(f"Используем полиномиальную аппроксимацию степени {optimal_degree}, R² = {r_squared:.3f}")
                except Exception as e:
                    print(f"Полиномиальная аппроксимация не удалась: {e}")
            
            # Метод 2: Если полиномиальная не подошла, используем сплайн-интерполяцию
            if not success_poly:
                try:
                    # Убираем дубликаты по времени для сплайна
                    unique_indices = []
                    seen_times = set()
                    for i, t in enumerate(timestamps):
                        if t not in seen_times:
                            unique_indices.append(i)
                            seen_times.add(t)
                    
                    if len(unique_indices) >= 3:
                        unique_timestamps = timestamps[unique_indices]
                        unique_values = values[unique_indices]
                        
                        # Используем UnivariateSpline для гладкой кривой
                        k = min(3, len(unique_timestamps) - 1)  # Степень сплайна
                        s = len(unique_timestamps) * 0.1  # Параметр сглаживания
                        
                        spline = UnivariateSpline(unique_timestamps, unique_values, k=k, s=s)
                        chosen_method = "spline"
                        print(f"Используем сплайн-интерполяцию степени {k}")
                    else:
                        # Простая линейная интерполяция
                        interp_func = interp1d(timestamps, values, kind='linear', 
                                             bounds_error=False, fill_value='extrapolate')
                        chosen_method = "linear"
                        print("Используем линейную интерполяцию")
                        
                except Exception as e:
                    print(f"Сплайн-интерполяция не удалась: {e}")
                    # Fallback к линейной интерполяции
                    interp_func = interp1d(timestamps, values, kind='linear', 
                                         bounds_error=False, fill_value='extrapolate')
                    chosen_method = "linear"
            
            # Создаем гладкую кривую СТРОГО в рамках запрошенного периода
            # Определяем временные границы на основе запрошенного периода, а не данных
            current_time = datetime.utcnow()
            period_start = current_time - timedelta(hours=hours_back)
            
            # Время в минутах от базового времени
            min_time = (period_start - base_time).total_seconds() / 60
            max_time = (current_time - base_time).total_seconds() / 60
            
            print(f"Границы аппроксимации: {min_time:.1f} - {max_time:.1f} минут (период {hours_back}ч)")
            print(f"Границы данных: {timestamps.min():.1f} - {timestamps.max():.1f} минут")
            
            # Преобразуем обратно в datetime для фронтенда
            smooth_datetimes = []
            for t in smooth_timestamps:
                dt = base_time + timedelta(minutes=float(t))
                smooth_datetimes.append(dt.isoformat())
            
            # Вычисляем значения аппроксимации
            if chosen_method == "polynomial" and success_poly:
                smooth_values = poly_model.predict(smooth_timestamps.reshape(-1, 1))
                quality_score = r_squared
            elif chosen_method == "spline":
                smooth_values = spline(smooth_timestamps)
                # Приблизительная оценка качества для сплайна
                predicted_original = spline(unique_timestamps)
                quality_score = 1 - np.mean((unique_values - predicted_original) ** 2) / np.var(unique_values)
            else:  # linear
                smooth_values = interp_func(smooth_timestamps)
                quality_score = 0.5  # Примерная оценка для линейной интерполяции
            
            # Преобразуем обратно в datetime для фронтенда
            smooth_datetimes = []
            for t in smooth_timestamps:
                dt = base_time + timedelta(minutes=float(t))
                smooth_datetimes.append(dt.isoformat())
            
            # Формируем исходные данные для фронтенда (только за запрошенный период)
            # original_data уже подготовлен выше
            
            # Формируем данные аппроксимации
            approximation_data = []
            for i, dt in enumerate(smooth_datetimes):
                approximation_data.append({
                    'timestamp': dt,
                    'value': float(smooth_values[i])
                })
            
            print(f"Аппроксимация успешна: метод={chosen_method}, качество={quality_score:.3f}")
            print(f"Исходных точек: {len(original_data)}, точек аппроксимации: {len(approximation_data)}")
            
            return {
                'original_data': original_data,
                'approximation': approximation_data,
                'quality_metrics': {
                    'method': chosen_method,
                    'quality_score': float(quality_score),
                    'degree': optimal_degree if chosen_method == "polynomial" else None,
                    'num_original_points': len(readings),  # Только за запрошенный период
                    'num_training_points': len(training_readings),  # Для обучения
                    'num_approximation_points': num_points,
                    'time_range_minutes': float(max_time - min_time),
                    'requested_hours': hours_back
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
    def get_trend_analysis(sensor_id, hours_back=1, degree=3):
        """
        Анализирует тренд на основе полиномиальной аппроксимации за последний час
        
        Returns:
            dict: анализ тренда (возрастающий, убывающий, стабильный)
        """
        approximation_data = ApproximationService.get_polynomial_approximation(
            sensor_id, hours_back, degree, 30  # 30 точек для анализа тренда
        )
        
        if approximation_data['error'] or len(approximation_data['approximation']) < 2:
            return {
                'trend': 'unknown',
                'trend_strength': 0,
                'description': 'Недостаточно данных для анализа тренда'
            }
        
        # Анализируем изменение значений по аппроксимации
        values = [point['value'] for point in approximation_data['approximation']]
        
        # Сравниваем начальные и конечные значения
        num_compare_points = max(3, len(values) // 5)  # Берем 20% точек с каждого конца
        
        start_values = np.mean(values[:num_compare_points])
        end_values = np.mean(values[-num_compare_points:])
        
        change = end_values - start_values
        change_percent = (change / abs(start_values)) * 100 if start_values != 0 else 0
        
        # Анализируем общую тенденцию через производную (скорость изменения)
        if len(values) > 5:
            # Вычисляем скользящее среднее изменений
            derivatives = np.diff(values)
            avg_derivative = np.mean(derivatives)
            derivative_trend = "increasing" if avg_derivative > 0 else "decreasing" if avg_derivative < 0 else "stable"
        else:
            derivative_trend = "unknown"
        
        # Более чувствительные пороги для часового анализа
        threshold_small = 1.0   # 1% для малых изменений
        threshold_large = 5.0   # 5% для больших изменений
        
        # Определяем тренд
        if abs(change_percent) < threshold_small:
            trend = 'stable'
            description = f'Показания стабильны за последний час (изменение {change_percent:+.1f}%)'
        elif change_percent > threshold_large:
            trend = 'strongly_increasing'
            description = f'Сильный рост показаний за час (+{change_percent:.1f}%)'
        elif change_percent > threshold_small:
            trend = 'increasing'
            description = f'Рост показаний за час (+{change_percent:.1f}%)'
        elif change_percent < -threshold_large:
            trend = 'strongly_decreasing'
            description = f'Сильное снижение показаний за час ({change_percent:.1f}%)'
        else:  # change_percent < -threshold_small
            trend = 'decreasing'
            description = f'Снижение показаний за час ({change_percent:.1f}%)'
        
        return {
            'trend': trend,
            'trend_strength': abs(change_percent),
            'change_percent': change_percent,
            'description': description,
            'start_value': start_values,
            'end_value': end_values,
            'derivative_trend': derivative_trend,
            'time_period_hours': hours_back
        }
    
    @staticmethod
    def get_optimal_degree(sensor_id, hours_back=1, max_degree=4):
        """
        Определяет оптимальную степень полинома для аппроксимации
        
        Returns:
            int: оптимальная степень полинома
        """
        # Получаем данные
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        readings = DataService.get_readings_for_period(sensor_id, start_time)
        
        if len(readings) < 4:
            return 2  # Минимальная степень для малого количества данных
        
        # Подготавливаем данные
        timestamps = []
        values = []
        
        readings = sorted(readings, key=lambda x: x.timestamp)
        base_time = readings[0].timestamp
        for reading in readings:
            time_diff = (reading.timestamp - base_time).total_seconds() / 60  # В минутах
            timestamps.append(time_diff)
            values.append(reading.value)
        
        timestamps = np.array(timestamps).reshape(-1, 1)
        values = np.array(values)
        
        best_degree = 2
        best_score = -float('inf')
        
        # Ограничиваем максимальную степень количеством данных
        max_allowed_degree = min(max_degree, len(readings) - 1)
        
        # Тестируем разные степени полинома
        for degree in range(2, max_allowed_degree + 1):
            try:
                poly_model = Pipeline([
                    ('poly', PolynomialFeatures(degree=degree)),
                    ('linear', LinearRegression())
                ])
                
                poly_model.fit(timestamps, values)
                score = poly_model.score(timestamps, values)
                
                # Штрафуем за переобучение
                penalty = (degree - 2) * 0.05  # 5% штрафа за каждую степень выше 2
                adjusted_score = score - penalty
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_degree = degree
                    
            except:
                continue
        
        print(f"Оптимальная степень полинома: {best_degree} (из {len(readings)} точек за {hours_back}ч)")
        return best_degree
    
    @staticmethod
    def get_hourly_smooth_curve(sensor_id, num_points=100):
        """
        Специальный метод для создания очень гладкой кривой за последний час
        
        Returns:
            dict: данные для построения гладкой кривой
        """
        return ApproximationService.get_polynomial_approximation(
            sensor_id=sensor_id,
            hours_back=1,
            degree=3,  # Кубический полином для гладкости
            num_points=num_points  # Много точек для гладкой кривой
        )