// client/src/components/BuildingDetails.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Button, Spinner } from 'react-bootstrap';
import { buildingsApi, sensorsApi } from '../services/api';
import SensorCard from './SensorCard';

const BuildingDetails = () => {
  const { buildingId } = useParams();
  const [building, setBuilding] = useState(null);
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBuildingData = async () => {
      try {
        setLoading(true);
        // Загружаем информацию о здании
        const buildingResponse = await buildingsApi.getById(buildingId);
        setBuilding(buildingResponse.data);
        
        // Загружаем датчики для этого здания
        const sensorsResponse = await sensorsApi.getAll(buildingId);
        setSensors(sensorsResponse.data);
        
        setError(null);
      } catch (err) {
        console.error('Ошибка загрузки данных здания:', err);
        setError('Не удалось загрузить данные здания. Проверьте соединение с сервером.');
      } finally {
        setLoading(false);
      }
    };

    fetchBuildingData();
  }, [buildingId]);

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Загрузка...</span>
        </Spinner>
        <p className="mt-2">Загрузка данных здания...</p>
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

  if (!building) {
    return (
      <Container className="mt-5">
        <Alert variant="warning">
          <Alert.Heading>Здание не найдено</Alert.Heading>
          <p>Здание с ID {buildingId} не найдено.</p>
          <div className="d-flex justify-content-end">
            <Link to="/">
              <Button variant="outline-primary">Вернуться на дашборд</Button>
            </Link>
          </div>
        </Alert>
      </Container>
    );
  }

  // Проверяем, есть ли датчики в состоянии тревоги
  const hasAlerts = sensors.some(
    sensor => sensor.last_reading && sensor.last_reading.is_alert
  );

  return (
    <Container fluid>
      <div className="d-flex align-items-center mb-4">
        <Link to="/" className="me-3">
          <Button variant="outline-secondary" size="sm">← Назад</Button>
        </Link>
        <h1 className="mb-0">{building.name}</h1>
      </div>

      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header as="h5">Информация о здании</Card.Header>
            <Card.Body>
              <Row>
                <Col sm={4} className="fw-bold">Адрес:</Col>
                <Col sm={8}>{building.address}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={4} className="fw-bold">Тип здания:</Col>
                <Col sm={8}>{building.building_type || 'Не указан'}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={4} className="fw-bold">Этажей:</Col>
                <Col sm={8}>{building.floors || 'Не указано'}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={4} className="fw-bold">Год постройки:</Col>
                <Col sm={8}>{building.construction_year || 'Не указан'}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={4} className="fw-bold">Количество датчиков:</Col>
                <Col sm={8}>{sensors.length}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={4} className="fw-bold">Статус:</Col>
                <Col sm={8}>
                  {hasAlerts ? (
                    <Alert variant="danger" className="py-1 px-2 mb-0 d-inline-block">
                      Требует внимания
                    </Alert>
                  ) : (
                    <Alert variant="success" className="py-1 px-2 mb-0 d-inline-block">
                      В норме
                    </Alert>
                  )}
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          {/* Здесь можно добавить блок для схемы здания или другой информации */}
          <Card>
            <Card.Header as="h5">Состояние мониторинга</Card.Header>
            <Card.Body>
              <p className="mb-2">
                <strong>Активных датчиков:</strong> {sensors.filter(s => s.status === 'active').length} из {sensors.length}
              </p>
              <p className="mb-2">
                <strong>Тревог:</strong> {sensors.filter(s => s.last_reading && s.last_reading.is_alert).length}
              </p>
              <p className="mb-3">
                <strong>Последнее обновление:</strong> {new Date().toLocaleString()}
              </p>
              
              <Button variant="primary" onClick={() => window.location.reload()}>
                Обновить данные
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <h2 className="mb-3">Датчики</h2>
      {hasAlerts && (
        <Alert variant="warning" className="mb-4">
          <Alert.Heading>Внимание!</Alert.Heading>
          <p>
            Один или несколько датчиков показывают значения за пределами нормы. Требуется проверка.
          </p>
        </Alert>
      )}

      <Row>
        {sensors.map((sensor) => (
          <Col key={sensor.id} md={6} lg={4} xl={3} className="mb-4">
            <SensorCard sensor={sensor} />
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default BuildingDetails;