// client/src/components/ApproximationView.js (УПРОЩЕННАЯ ВЕРСИЯ)
import React from 'react';
import { Card, Alert, Badge, Row, Col } from 'react-bootstrap';
import { FaChartLine, FaArrowUp, FaArrowDown, FaMinus } from 'react-icons/fa';

const ApproximationView = ({ approximationData, trendAnalysis, unit, sensorType }) => {
  
  // Если нет данных
  if (!approximationData) {
    return (
      <Card className="mt-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Анализ данных
        </Card.Header>
        <Card.Body>
          <Alert variant="info">Загрузка данных...</Alert>
        </Card.Body>
      </Card>
    );
  }

  // Если есть ошибка
  if (approximationData.error) {
    return (
      <Card className="mt-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Анализ данных
        </Card.Header>
        <Card.Body>
          <Alert variant="warning">
            <Alert.Heading>Недостаточно данных</Alert.Heading>
            <p>{approximationData.error}</p>
            <p className="mb-0">
              <strong>Попробуйте:</strong>
            </p>
            <ul>
              <li>Увеличить период анализа</li>
              <li>Дождаться накопления данных</li>
              <li>Проверить работу датчика</li>
            </ul>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // Получаем метрики качества
  const quality = approximationData.quality_metrics || {};
  const rSquared = quality.r_squared || 0;
  const degree = quality.degree || 'неизвестно';
  const originalPoints = quality.num_original_points || 0;

  // Определяем качество аппроксимации
  const getQualityBadge = (score) => {
    if (score >= 0.9) return { variant: 'success', text: 'Отличное' };
    if (score >= 0.7) return { variant: 'primary', text: 'Хорошее' };
    if (score >= 0.5) return { variant: 'warning', text: 'Удовлетворительное' };
    return { variant: 'danger', text: 'Плохое' };
  };

  const qualityBadge = getQualityBadge(rSquared);

  // Иконки для трендов
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
      case 'strongly_increasing':
        return <FaArrowUp className="text-warning" />;
      case 'decreasing':
      case 'strongly_decreasing':
        return <FaArrowDown className="text-primary" />;
      default:
        return <FaMinus className="text-success" />;
    }
  };

  const getTrendBadge = (trend) => {
    switch (trend) {
      case 'strongly_increasing': return 'danger';
      case 'increasing': return 'warning';
      case 'decreasing': return 'primary';
      case 'strongly_decreasing': return 'info';
      default: return 'success';
    }
  };

  return (
    <Card className="mt-4">
      <Card.Header as="h5">
        <FaChartLine className="me-2" />
        Анализ данных с аппроксимацией
      </Card.Header>
      <Card.Body>
        
        {/* Тренд и качество */}
        <Row className="mb-3">
          <Col md={6}>
            <h6>Тренд показаний:</h6>
            <div className="d-flex align-items-center">
              {getTrendIcon(trendAnalysis?.trend)}
              <Badge bg={getTrendBadge(trendAnalysis?.trend)} className="ms-2">
                {trendAnalysis?.description || 'Анализируется...'}
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
            <Badge bg={qualityBadge.variant}>
              {qualityBadge.text} ({(rSquared * 100).toFixed(1)}%)
            </Badge>
            <br />
            <small className="text-muted">
              Полином {degree}-й степени
            </small>
          </Col>
        </Row>

        {/* Информация о данных */}
        <Row className="mb-3">
          <Col md={6}>
            <small className="text-muted">
              <strong>Период анализа:</strong> {quality.requested_hours || 24} часов
            </small>
            <br />
            <small className="text-muted">
              <strong>Точек данных:</strong> {originalPoints}
            </small>
          </Col>
          <Col md={6}>
            {trendAnalysis?.start_value && trendAnalysis?.end_value && (
              <>
                <small className="text-muted">
                  <strong>Начало:</strong> {trendAnalysis.start_value.toFixed(2)} {unit}
                </small>
                <br />
                <small className="text-muted">
                  <strong>Сейчас:</strong> {trendAnalysis.end_value.toFixed(2)} {unit}
                </small>
              </>
            )}
          </Col>
        </Row>

        {/* Предупреждения */}
        {trendAnalysis?.trend === 'strongly_increasing' && (
          <Alert variant="warning">
            <FaArrowUp className="me-2" />
            <strong>Внимание!</strong> Сильный рост показаний {sensorType}. 
            Рекомендуется проверка.
          </Alert>
        )}

        {trendAnalysis?.trend === 'strongly_decreasing' && (
          <Alert variant="info">
            <FaArrowDown className="me-2" />
            <strong>Информация:</strong> Значительное снижение показаний {sensorType}.
          </Alert>
        )}

        {rSquared < 0.5 && (
          <Alert variant="secondary">
            <strong>Примечание:</strong> Низкое качество аппроксимации может указывать 
            на высокий уровень шумов или нестабильность {sensorType}.
          </Alert>
        )}

      </Card.Body>
    </Card>
  );
};

export default ApproximationView;