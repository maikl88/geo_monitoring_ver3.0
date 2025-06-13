// client/src/components/ApproximationView.js (исправленная версия)
import React from 'react';
import { Card, Alert, Badge, Row, Col } from 'react-bootstrap';
import { FaChartLine, FaArrowUp, FaArrowDown, FaMinus } from 'react-icons/fa';

const ApproximationView = ({ approximationData, trendAnalysis, unit, sensorType }) => {
  // Показываем информацию даже при частичных ошибках
  if (!approximationData) {
    return (
      <Card className="sensor-details-card mt-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Анализ данных с аппроксимацией
        </Card.Header>
        <Card.Body>
          <Alert variant="info">
            Загрузка данных для аппроксимации...
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  if (approximationData.error) {
    return (
      <Card className="sensor-details-card mt-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Анализ данных с аппроксимацией
        </Card.Header>
        <Card.Body>
          <Alert variant="warning">
            <Alert.Heading>Недостаточно данных</Alert.Heading>
            <p>{approximationData.error}</p>
            <hr />
            <p className="mb-0">
              <strong>Рекомендации:</strong>
              <ul className="mt-2">
                <li>Увеличьте период анализа данных</li>
                <li>Дождитесь накопления большего количества показаний</li>
                <li>Проверьте работу датчика и поступление данных</li>
              </ul>
            </p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // Получаем данные о качестве аппроксимации
  const qualityMetrics = approximationData.quality_metrics || {};
  
  // Поддерживаем как старые, так и новые поля
  const qualityScore = qualityMetrics.quality_score || qualityMetrics.r_squared || 0;
  const method = qualityMetrics.method || 'polynomial';
  const degree = qualityMetrics.degree || 'неизвестно';
  const originalPoints = qualityMetrics.num_original_points || 0;
  const trainingPoints = qualityMetrics.num_training_points || originalPoints;
  const requestedHours = qualityMetrics.requested_hours || 1;

  // Определяем качество аппроксимации
  const getQualityInfo = (score) => {
    if (score >= 0.9) {
      return { variant: 'success', text: 'Отличное' };
    } else if (score >= 0.8) {
      return { variant: 'primary', text: 'Хорошее' };
    } else if (score >= 0.6) {
      return { variant: 'warning', text: 'Удовлетворительное' };
    } else {
      return { variant: 'danger', text: 'Плохое' };
    }
  };

  const qualityInfo = getQualityInfo(qualityScore);

  // Определяем текст метода аппроксимации
  const getMethodText = (method) => {
    switch (method) {
      case 'polynomial':
        return `Полином ${degree}-й степени`;
      case 'spline':
        return 'Сплайн-интерполяция';
      case 'linear':
        return 'Линейная интерполяция';
      default:
        return `${method} (степень ${degree})`;
    }
  };

  // Определяем иконку и цвет для тренда
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
      case 'strongly_increasing':
        return <FaArrowUp className="text-warning" />;
      case 'decreasing':
      case 'strongly_decreasing':
        return <FaArrowDown className="text-primary" />;
      case 'stable':
      default:
        return <FaMinus className="text-success" />;
    }
  };

  const getTrendVariant = (trend) => {
    switch (trend) {
      case 'strongly_increasing':
        return 'danger';
      case 'increasing':
        return 'warning';
      case 'decreasing':
        return 'primary';
      case 'strongly_decreasing':
        return 'info';
      case 'stable':
      default:
        return 'success';
    }
  };

  return (
    <Card className="sensor-details-card mt-4">
      <Card.Header as="h5">
        <FaChartLine className="me-2" />
        Анализ данных с аппроксимацией
      </Card.Header>
      <Card.Body>
        {/* Информация о тренде */}
        <Row className="mb-3">
          <Col md={6}>
            <h6>Тренд показаний:</h6>
            <div className="d-flex align-items-center">
              {getTrendIcon(trendAnalysis?.trend)}
              <Badge bg={getTrendVariant(trendAnalysis?.trend)} className="ms-2">
                {trendAnalysis?.description || 'Данные обрабатываются...'}
              </Badge>
            </div>
            {trendAnalysis?.change_percent && (
              <small className="text-muted">
                Изменение: {trendAnalysis.change_percent > 0 ? '+' : ''}{trendAnalysis.change_percent.toFixed(1)}%
              </small>
            )}
          </Col>
          
          <Col md={6}>
            <h6>Качество аппроксимации:</h6>
            <Badge bg={qualityInfo.variant}>
              {qualityInfo.text} (R² = {(qualityScore * 100).toFixed(1)}%)
            </Badge>
            <br />
            <small className="text-muted">
              {getMethodText(method)}
            </small>
          </Col>
        </Row>

        {/* Информация о данных */}
        <Row className="mb-3">
          <Col md={6}>
            <small className="text-muted">
              <strong>Данные за период:</strong> {requestedHours}ч ({originalPoints} точек)
            </small>
            {trainingPoints > originalPoints && (
              <><br />
              <small className="text-muted">
                <strong>Для обучения использовано:</strong> {trainingPoints} точек
              </small></>
            )}
          </Col>
          <Col md={6}>
            <small className="text-muted">
              <strong>Метод аппроксимации:</strong> {method}
            </small>
          </Col>
        </Row>

        {/* Дополнительная информация о значениях */}
        {trendAnalysis && (
          <Row className="mb-3">
            <Col md={6}>
              <small className="text-muted">
                <strong>Начальное значение:</strong> {trendAnalysis.start_value?.toFixed(2)} {unit}
              </small>
            </Col>
            <Col md={6}>
              <small className="text-muted">
                <strong>Текущее значение:</strong> {trendAnalysis.end_value?.toFixed(2)} {unit}
              </small>
            </Col>
          </Row>
        )}

        {/* Предупреждения на основе тренда */}
        {trendAnalysis?.trend === 'strongly_increasing' && (
          <Alert variant="warning" className="approximation-alert">
            <div className="d-flex align-items-center">
              <FaArrowUp className="me-2" />
              <div>
                <strong>Внимание!</strong> Наблюдается сильный рост показаний {sensorType}.
                Рекомендуется дополнительная проверка системы.
              </div>
            </div>
          </Alert>
        )}

        {trendAnalysis?.trend === 'strongly_decreasing' && (
          <Alert variant="info" className="approximation-alert">
            <div className="d-flex align-items-center">
              <FaArrowDown className="me-2" />
              <div>
                <strong>Информация:</strong> Наблюдается значительное снижение показаний {sensorType}.
                Это может указывать на изменение условий работы датчика.
              </div>
            </div>
          </Alert>
        )}

        {/* Информация о качестве данных */}
        {qualityScore < 0.6 && (
          <Alert variant="secondary" className="approximation-alert">
            <div>
              <strong>Примечание:</strong> Низкое качество аппроксимации может указывать на высокий уровень шумов 
              в данных или нестабильную работу датчика. Рекомендуется увеличить период анализа или 
              проверить техническое состояние {sensorType}.
            </div>
          </Alert>
        )}

        {/* Информация о методе интерполяции для случаев с малым количеством данных */}
        {method !== 'polynomial' && (
          <Alert variant="info" className="approximation-alert">
            <div>
              <strong>Информация:</strong> Из-за недостаточного количества данных использована {method === 'spline' ? 'сплайн-интерполяция' : 'линейная интерполяция'} 
              вместо полиномиальной аппроксимации. Для более точного анализа рекомендуется увеличить период сбора данных.
            </div>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default ApproximationView;