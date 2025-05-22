// client/src/components/SensorChart.js (обновленная версия)
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
import { ru } from 'date-fns/locale';

// Регистрируем необходимые компоненты ChartJS
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
  // Подготавливаем исходные данные для графика
  const formatReadingsData = () => {
    if (!readings || readings.length === 0) {
      return [];
    }

    return readings.map(reading => ({
      x: new Date(reading.timestamp),
      y: reading.value
    }));
  };

  // Подготавливаем данные аппроксимации
  const formatApproximationData = () => {
    if (!approximationData || !approximationData.approximation || approximationData.approximation.length === 0) {
      return [];
    }

    return approximationData.approximation.map(point => ({
      x: new Date(point.timestamp),
      y: point.value
    }));
  };

  // Настройки для графика
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
            hour: 'HH:mm'
          }
        },
        title: {
          display: true,
          text: 'Время'
        },
        adapters: {
          date: {
            locale: ru
          }
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
        position: 'top',
      },
      title: {
        display: true,
        text: `Показания ${sensorType || 'датчика'} с полиномиальной аппроксимацией`
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += `${context.parsed.y.toFixed(2)} ${unit || ''}`;
            }
            return label;
          }
        }
      }
    }
  };

  // Данные для графика
  const datasets = [];

  // Добавляем исходные данные (точки датчика)
  const readingsData = formatReadingsData();
  if (readingsData.length > 0) {
    datasets.push({
      label: 'Данные датчика',
      data: readingsData,
      borderColor: 'rgba(75, 192, 192, 0.6)',
      backgroundColor: 'rgba(75, 192, 192, 0.8)',
      pointRadius: 3,
      pointHoverRadius: 5,
      borderWidth: 1,
      tension: 0, // Прямые линии между точками
      showLine: true
    });
  }

  // Добавляем аппроксимацию (гладкая кривая)
  const approximationPoints = formatApproximationData();
  if (approximationPoints.length > 0) {
    datasets.push({
      label: `Аппроксимация (степень ${approximationData?.quality_metrics?.degree || 'авто'})`,
      data: approximationPoints,
      borderColor: 'rgba(255, 99, 132, 0.8)',
      backgroundColor: 'rgba(255, 99, 132, 0.1)',
      pointRadius: 0, // Убираем точки для гладкой кривой
      pointHoverRadius: 3,
      borderWidth: 3,
      tension: 0.1, // Небольшая сглаженность
      fill: false
    });
  }

  const data = {
    datasets: datasets
  };

  // Если нет данных для отображения
  if (datasets.length === 0) {
    return (
      <Card className="chart-container">
        <Card.Body>
          <div className="text-center p-4">
            <p className="text-muted">Нет данных для отображения графика</p>
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
        {/* Показываем информацию о качестве аппроксимации под графиком */}
        {approximationData?.quality_metrics && (
          <div className="mt-3 text-center">
            <small className="text-muted">
              Полином {approximationData.quality_metrics.degree}-й степени | 
              Точность: R² = {(approximationData.quality_metrics.r_squared * 100).toFixed(1)}% | 
              Точек данных: {approximationData.quality_metrics.num_original_points} | 
              Точек аппроксимации: {approximationData.quality_metrics.num_approximation_points}
            </small>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default SensorChart;