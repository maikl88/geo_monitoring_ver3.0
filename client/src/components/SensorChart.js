// client/src/components/SensorChart.js (С ЖИРНОЙ АППРОКСИМАЦИЕЙ ПОВЕРХ)

import React from 'react';
import { Card } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const SensorChart = ({ readings, approximationData, sensorType, unit }) => {
  
  // Функция для нормализации времени
  const normalizeTime = (timestamp) => {
    const cleanTime = timestamp.replace('Z', '');
    return new Date(cleanTime + 'Z');
  };

  // Подготавливаем данные показаний
  const formatReadingsData = () => {
    if (!readings || readings.length === 0) return [];
    
    return readings.map(reading => ({
      x: normalizeTime(reading.timestamp),
      y: reading.value
    }));
  };

  // Подготавливаем данные аппроксимации
  const formatApproximationData = () => {
    if (!approximationData || !approximationData.approximation || approximationData.approximation.length === 0) {
      return [];
    }

    return approximationData.approximation.map(point => ({
      x: normalizeTime(point.timestamp),
      y: point.value
    }));
  };

  // Настройки графика
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'hour',
          tooltipFormat: 'dd.MM.yyyy HH:mm',
          displayFormats: {
            hour: 'HH:mm',
            day: 'dd.MM'
          }
        },
        title: {
          display: true,
          text: 'Время'
        }
      },
      y: {
        title: {
          display: true,
          text: unit || 'Значение'
        }
      }
    },
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: `Показания ${sensorType || 'датчика'}`
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || '';
            const value = context.parsed.y?.toFixed(2) || 'N/A';
            return `${label}: ${value} ${unit || ''}`;
          }
        }
      }
    }
  };

  // Готовим данные для графика
  const datasets = [];
  
  // 1. СНАЧАЛА добавляем исходные данные (будут ПОД аппроксимацией)
  const readingsData = formatReadingsData();
  if (readingsData.length > 0) {
    datasets.push({
      label: 'Данные датчика',
      data: readingsData,
      borderColor: 'rgba(75, 192, 192, 0.7)',        // Более прозрачный
      backgroundColor: 'rgba(75, 192, 192, 0.2)',     // Очень прозрачный
      pointRadius: 2,                                  // Меньше точки
      pointHoverRadius: 4,
      borderWidth: 1,                                  // Тонкая линия
      tension: 0,
      order: 2                                         // ⭐ Порядок отрисовки: 2 = под аппроксимацией
    });
  }

  // 2. ПОТОМ добавляем аппроксимацию (будет ПОВЕРХ данных)
  const approximationPoints = formatApproximationData();
  if (approximationPoints.length > 0) {
    const degree = approximationData?.quality_metrics?.degree || 'авто';
    datasets.push({
      label: `Аппроксимация (степень ${degree})`,
      data: approximationPoints,
      borderColor: 'rgba(220, 53, 69, 1)',            // ⭐ Яркий красный, непрозрачный
      backgroundColor: 'rgba(220, 53, 69, 0.1)',      // Слабая заливка
      pointRadius: 0,                                  // Без точек для гладкости
      pointHoverRadius: 0,
      borderWidth: 4,                                  // ⭐ ЖИРНАЯ линия (было 3)
      tension: 0.1,
      fill: false,
      order: 1                                         // ⭐ Порядок отрисовки: 1 = поверх данных
    });
  }

  const data = { datasets };

  // Если нет данных
  if (datasets.length === 0) {
    return (
      <Card className="chart-container">
        <Card.Body>
          <div className="text-center p-4">
            <p className="text-muted">Нет данных для отображения</p>
          </div>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="chart-container">
      <Card.Body>
        <div style={{ height: '400px' }}>
          <Line options={options} data={data} />
        </div>
        {/* Информация о качестве */}
        {approximationData?.quality_metrics && (
          <div className="mt-3 text-center">
            <small className="text-muted">
              <span style={{ color: '#dc3545', fontWeight: 'bold' }}>━━</span> Полином {approximationData.quality_metrics.degree}-й степени | 
              R² = {(approximationData.quality_metrics.r_squared * 100).toFixed(1)}% | 
              Точек: {approximationData.quality_metrics.num_original_points}
            </small>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default SensorChart;