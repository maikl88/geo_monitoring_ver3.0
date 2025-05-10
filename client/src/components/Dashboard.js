// client/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { buildingsApi, alertsApi, utilsApi } from '../services/api';
import SensorCard from './SensorCard';
import AlertsList from './AlertsList';

const Dashboard = () => {
  const [buildings, setBuildings] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataInitialized, setDataInitialized] = useState(false);

  // Загрузка зданий при монтировании компонента
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Загрузка данных для дашборда
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Загружаем здания
      const buildingsResponse = await buildingsApi.getAll();
      setBuildings(buildingsResponse.data);
      
      // Загружаем тревоги
      const alertsResponse = await alertsApi.getAll(24); // за последние 24 часа
      setAlerts(alertsResponse.data);
      
      setError(null);
    } catch (err) {
      console.error('Ошибка загрузки данных дашборда:', err);
      setError('Не удалось загрузить данные. Проверьте соединение с сервером.');
    } finally {
      setLoading(false);
    }
  };

  // Инициализация тестовых данных
  const initializeTestData = async () => {
    try {
      setLoading(true);
      const response = await utilsApi.initSampleData();
      console.log('Инициализация данных:', response.data);
      alert('Тестовые данные успешно инициализированы!');
      setDataInitialized(true);
      
      // Перезагружаем данные
      await loadDashboardData();
    } catch (err) {
      console.error('Ошибка инициализации данных:', err);
      setError('Не удалось инициализировать тестовые данные.');
    } finally {
      setLoading(false);
    }
  };

  // Отображаем загрузку
  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Загрузка...</span>
        </Spinner>
        <p className="mt-2">Загрузка данных...</p>
      </Container>
    );
  }

  // Отображаем ошибку, если она есть
  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <Alert.Heading>Ошибка</Alert.Heading>
          <p>{error}</p>
          {!dataInitialized && (
            <div className="d-flex justify-content-end">
              <Button onClick={initializeTestData} variant="outline-danger">
                Инициализировать тестовые данные
              </Button>
            </div>
          )}
        </Alert>
      </Container>
    );
  }

  // Если нет зданий, предлагаем инициализировать данные
  if (buildings.length === 0) {
    return (
      <Container className="mt-5">
        <Alert variant="info">
          <Alert.Heading>Нет данных</Alert.Heading>
          <p>В системе нет зданий для мониторинга.</p>
          <div className="d-flex justify-content-end">
            <Button onClick={initializeTestData} variant="outline-primary">
              Инициализировать тестовые данные
            </Button>
          </div>
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="dashboard-container">
      <Row className="mb-4">
        <Col>
          <h1>Дашборд геотехнического мониторинга</h1>
          <p className="text-muted">
            Мониторинг {buildings.length} зданий | {alerts.length} активных тревог
          </p>
        </Col>
        <Col md="auto">
          <Button variant="primary" onClick={loadDashboardData}>
            Обновить данные
          </Button>
        </Col>
      </Row>

      {/* Блок тревог */}
      {alerts.length > 0 && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header as="h5" className="bg-danger text-white">
                Активные тревоги
              </Card.Header>
              <Card.Body>
                <AlertsList alerts={alerts} />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Блок зданий */}
      <h2 className="mb-3">Здания под мониторингом</h2>
      <Row>
        {buildings.map((building) => (
          <Col key={building.id} md={6} lg={4} className="mb-4">
            <Card className="building-card h-100">
              <Card.Header as="h5">{building.name}</Card.Header>
              <Card.Body>
                <Card.Text>
                  <strong>Адрес:</strong> {building.address}<br />
                  <strong>Тип:</strong> {building.building_type || 'Не указан'}<br />
                  <strong>Этажей:</strong> {building.floors || 'Не указано'}
                </Card.Text>
                <Link to={`/buildings/${building.id}`}>
                  <Button variant="outline-primary">Подробнее</Button>
                </Link>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default Dashboard;