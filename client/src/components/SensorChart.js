// client/src/components/SensorChart.js
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

const SensorChart = ({ readings, predictions, sensorType, unit }) => {
  // Подготавливаем данные для графика
  const formatReadingsData = () => {
    if (!readings || readings.length === 0) {
      return [];
    }

    return readings.map(reading => ({
      x: new Date(reading.timestamp),
      y: reading.value
    }));
  };

  // Подготавливаем данные предсказаний
  const formatPredictionsData = () => {
    if (!predictions || predictions.length === 0) {
      return [];
    }

    return predictions.map(prediction => ({
      x: new Date(prediction.timestamp),
      y: prediction.value
    }));
  };

  // Настройки для графика
  const options = {
    responsive: true,
    maintainAspectRatio: false,
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
        text: `Показания ${sensorType || 'датчика'}`
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += `${context.parsed.y} ${unit || ''}`;
            }
            return label;
          }
        }
      }
    }
  };

  // Данные для графика
  const data = {
    datasets: [
      {
        label: 'Исторические данные',
        data: formatReadingsData(),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      }
    ]
  };

  // Добавляем предсказания, если они есть
  if (predictions && predictions.length > 0) {
    data.datasets.push({
      label: 'Предсказания',
      data: formatPredictionsData(),
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      borderDash: [5, 5] // Пунктирная линия для предсказаний
    });
  }

  return (
    <Card className="chart-container">
      <Card.Body>
        <div style={{ height: '400px' }}>
          <Line options={options} data={data} />
        </div>
      </Card.Body>
    </Card>
  );
};

export default SensorChart;