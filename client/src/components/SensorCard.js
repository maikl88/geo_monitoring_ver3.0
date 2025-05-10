// client/src/components/SensorCard.js
import React from 'react';
import { Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaThermometerHalf, FaTachometerAlt, FaRuler, FaExclamationTriangle } from 'react-icons/fa';

const SensorCard = ({ sensor }) => {
  // Определяем иконку в зависимости от типа датчика
  const getSensorIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'инклинометр':
        return <FaRuler size={24} />;
      case 'тензометр':
        return <FaRuler size={24} />;
      case 'акселерометр':
        return <FaTachometerAlt size={24} />;
      case 'датчик трещин':
        return <FaRuler size={24} />;
      case 'датчик температуры':
        return <FaThermometerHalf size={24} />;
      default:
        return <FaTachometerAlt size={24} />;
    }
  };

  // Определяем цвет карточки в зависимости от статуса
  const getCardVariant = () => {
    if (!sensor.last_reading) return 'light';
    
    if (sensor.last_reading.is_alert) {
      return 'danger';
    }
    
    if (sensor.status === 'maintenance') {
      return 'warning';
    }
    
    return 'light';
  };

  return (
    <Card 
      className="sensor-card" 
      border={getCardVariant() !== 'light' ? getCardVariant() : ''}
    >
      {sensor.last_reading && sensor.last_reading.is_alert && (
        <div className="alert-badge">
          <FaExclamationTriangle className="alert-marker" size={18} />
        </div>
      )}
      
      <Card.Body>
        <div className="d-flex align-items-center mb-3">
          <div className="me-3">
            {getSensorIcon(sensor.type)}
          </div>
          <div>
            <Card.Title className="mb-0">{sensor.name}</Card.Title>
            <small className="text-muted">{sensor.type}</small>
          </div>
        </div>
        
        <Card.Text>
          <strong>Расположение:</strong> {sensor.location}<br />
          {sensor.floor && <><strong>Этаж:</strong> {sensor.floor}<br /></>}
          <strong>Статус:</strong>{' '}
          <Badge bg={sensor.status === 'active' ? 'success' : 'warning'}>
            {sensor.status === 'active' ? 'Активен' : 'Обслуживание'}
          </Badge>
        </Card.Text>
        
        {sensor.last_reading && (
          <Card.Text>
            <strong>Последнее показание:</strong><br />
            <span className={sensor.last_reading.is_alert ? 'text-danger fw-bold' : ''}>
              {sensor.last_reading.value} {sensor.last_reading.unit}
            </span>
            <br />
            <small className="text-muted">
              {new Date(sensor.last_reading.timestamp).toLocaleString()}
            </small>
          </Card.Text>
        )}
      </Card.Body>
      <Card.Footer>
        <Link to={`/sensors/${sensor.id}`} className="text-decoration-none">
          Подробнее
        </Link>
      </Card.Footer>
    </Card>
  );
};

export default SensorCard;