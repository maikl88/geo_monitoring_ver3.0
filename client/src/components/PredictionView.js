// client/src/components/PredictionView.js
import React from 'react';
import { Card, Alert } from 'react-bootstrap';
import { FaChartLine, FaExclamationTriangle } from 'react-icons/fa';

const PredictionView = ({ predictions, unit, sensorType }) => {
  if (!predictions || predictions.length === 0) {
    return (
      <Card className="sensor-details-card mt-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Прогноз
        </Card.Header>
        <Card.Body>
          <Alert variant="info">
            Недостаточно данных для построения прогноза.
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // Получаем последнее значение показаний и первое предсказание
  const lastPrediction = predictions[predictions.length - 1];
  const firstPrediction = predictions[0];
  
  // Рассчитываем изменение
  const change = lastPrediction.value - firstPrediction.value;
  const changePercent = ((change / firstPrediction.value) * 100).toFixed(2);
  
  // Определяем тренд
  let trend = 'стабильный';
  let trendVariant = 'info';
  
  if (Math.abs(change) < 0.01) {
    trend = 'стабильный';
    trendVariant = 'info';
  } else if (change > 0) {
    trend = 'рост';
    trendVariant = 'warning';
  } else {
    trend = 'снижение';
    trendVariant = 'primary';
  }
  
  // Определяем, есть ли предупреждения в предсказаниях
  const willExceedLimits = Math.abs(changePercent) > 20;

  return (
    <Card className="sensor-details-card mt-4">
      <Card.Header as="h5">
        <FaChartLine className="me-2" />
        Прогноз на следующие 24 часа
      </Card.Header>
      <Card.Body>
        <p>
          <strong>Текущий тренд:</strong>{' '}
          <Alert variant={trendVariant} className="py-1 px-2 mb-0 d-inline-block">
            {trend}
          </Alert>
        </p>
        
        <p>
          <strong>Прогнозируемое изменение:</strong>{' '}
          <span className={change > 0 ? 'text-danger' : change < 0 ? 'text-primary' : ''}>
            {change > 0 ? '+' : ''}{change.toFixed(2)} {unit} ({change > 0 ? '+' : ''}{changePercent}%)
          </span>
        </p>
        
        <p>
          <strong>Ожидаемое значение через 24 часа:</strong>{' '}
          <span className="fw-bold">
            {lastPrediction.value.toFixed(2)} {unit}
          </span>
        </p>
        
        {willExceedLimits && (
          <Alert variant="warning" className="prediction-alert">
            <div className="d-flex align-items-center">
              <FaExclamationTriangle className="me-2" />
              <div>
                <strong>Внимание!</strong> Прогнозируется значительное изменение показаний.
                Рекомендуется дополнительная проверка {sensorType}.
              </div>
            </div>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default PredictionView;