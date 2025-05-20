// client/src/components/SensorDetails.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Button, Badge, Spinner, Form } from 'react-bootstrap';
import { sensorsApi } from '../services/api';
import SensorChart from './SensorChart';
import PredictionView from './PredictionView';

const SensorDetails = () => {
  const { sensorId } = useParams();
  const [sensor, setSensor] = useState(null);
  const [readings, setReadings] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(24); // По умолчанию 24 часа

   // Добавьте эти состояния для автообновления
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5); // 5 секунд по умолчанию

  // Модифицированный useEffect, чтобы добавить автообновление
  useEffect(() => {
    // Загружаем данные при первой загрузке
    fetchSensorData();
    
    // Настраиваем интервал автообновления
    let intervalId = null;
    if (autoRefresh) {
      console.log(`Установка автообновления с интервалом ${refreshInterval} секунд`);
      intervalId = setInterval(() => {
        console.log("Автоматическое обновление данных...");
        fetchSensorData();
      }, refreshInterval * 1000);
    }
    
    // Очищаем интервал при размонтировании компонента или при изменении зависимостей
    return () => {
      if (intervalId) {
        console.log("Очистка интервала автообновления");
        clearInterval(intervalId);
      }
    };
  }, [sensorId, timeRange, autoRefresh, refreshInterval]); // Добавить autoRefresh и refreshInterval в зависимости

  const fetchSensorData = async () => {
    try {
      setLoading(true);
      // Загружаем информацию о датчике
      const sensorResponse = await sensorsApi.getById(sensorId);
      setSensor(sensorResponse.data);
      
      // Загружаем показания датчика
      const readingsResponse = await sensorsApi.getReadings(sensorId, timeRange);
      setReadings(readingsResponse.data);
      
      // Загружаем предсказания для датчика
      const predictionsResponse = await sensorsApi.getPredictions(sensorId, 24); // Всегда на 24 часа вперед
      setPredictions(predictionsResponse.data.predictions);
      
      setError(null);
    } catch (err) {
      console.error('Ошибка загрузки данных датчика:', err);
      setError('Не удалось загрузить данные датчика. Проверьте соединение с сервером.');
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (e) => {
    setTimeRange(parseInt(e.target.value));
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Загрузка...</span>
        </Spinner>
        <p className="mt-2">Загрузка данных датчика...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <Alert.Heading>Ошибка</Alert.Heading>
          <p>{error}</p>
          <div className="d-flex justify-content-end">
            <Link to="/">
              <Button variant="outline-danger">Вернуться на дашборд</Button>
            </Link>
          </div>
        </Alert>
      </Container>
    );
  }

  if (!sensor) {
    return (
      <Container className="mt-5">
        <Alert variant="warning">
          <Alert.Heading>Датчик не найден</Alert.Heading>
          <p>Датчик с ID {sensorId} не найден.</p>
          <div className="d-flex justify-content-end">
            <Link to="/">
              <Button variant="outline-primary">Вернуться на дашборд</Button>
            </Link>
          </div>
        </Alert>
      </Container>
    );
  }

  // Определяем единицу измерения
  const unit = sensor.last_reading ? sensor.last_reading.unit : '';

  return (
    <Container fluid>
      <div className="d-flex align-items-center mb-4">
        <Link to={`/buildings/${sensor.building_id}`} className="me-3">
          <Button variant="outline-secondary" size="sm">← Назад к зданию</Button>
        </Link>
        <h1 className="mb-0">{sensor.name}</h1>
      </div>

      <Row className="mb-4">
              <Col lg={6}>
        <Card className="sensor-details-card">
          <Card.Header as="h5">Настройки графика</Card.Header>
          <Card.Body>
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Период отображения данных</Form.Label>
                <Form.Select value={timeRange} onChange={handleTimeRangeChange}>
                  <option value="6">Последние 6 часов</option>
                  <option value="12">Последние 12 часов</option>
                  <option value="24">Последние 24 часа</option>
                  <option value="48">Последние 2 дня</option>
                  <option value="72">Последние 3 дня</option>
                  <option value="168">Последняя неделя</option>
                  <option value="720">Последний месяц</option>
                </Form.Select>
              </Form.Group>
              
              {/* Добавьте переключатель автообновления */}
              <Form.Group className="mb-3">
                <Form.Check 
                  type="switch"
                  id="auto-refresh-switch"
                  label="Автоматическое обновление"
                  checked={autoRefresh}
                  onChange={() => setAutoRefresh(!autoRefresh)}
                />
              </Form.Group>
              
              {/* Отображаем выбор интервала только если автообновление включено */}
              {autoRefresh && (
                <Form.Group className="mb-3">
                  <Form.Label>Интервал обновления (секунды)</Form.Label>
                  <Form.Select 
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(Number(e.target.value))}
                  >
                    <option value="5">5 секунд</option>
                    <option value="10">10 секунд</option>
                    <option value="30">30 секунд</option>
                    <option value="60">1 минута</option>
                  </Form.Select>
                </Form.Group>
              )}
              
              <Button variant="primary" onClick={fetchSensorData}>
                Обновить данные сейчас
              </Button>
            </Form>
          </Card.Body>
        </Card>
          
          {/* Блок предсказания */}
          <PredictionView 
            predictions={predictions} 
            unit={unit} 
            sensorType={sensor.type}
          />
        </Col>
      </Row>

      <Row>
        <Col>
          <h2 className="mb-3">График показаний</h2>
          <SensorChart 
            readings={readings} 
            predictions={predictions} 
            sensorType={sensor.type}
            unit={unit}
          />
        </Col>
      </Row>
    </Container>
  );
};

export default SensorDetails;