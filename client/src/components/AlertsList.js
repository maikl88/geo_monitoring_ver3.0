// client/src/components/AlertsList.js
import React from 'react';
import { Table, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaExclamationTriangle } from 'react-icons/fa';

const AlertsList = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return <p>Нет активных тревог.</p>;
  }

  return (
    <Table striped hover responsive>
      <thead>
        <tr>
          <th>Тревога</th>
          <th>Датчик</th>
          <th>Значение</th>
          <th>Время</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((alert) => (
          <tr key={alert.id}>
            <td>
              <FaExclamationTriangle className="text-danger me-2" />
            </td>
            <td>
              <Link to={`/sensors/${alert.sensor_id}`}>
                {alert.sensor_name}
              </Link>
            </td>
            <td>
              <Badge bg="danger">
                {alert.value} {alert.unit}
              </Badge>
            </td>
            <td>
              {new Date(alert.timestamp).toLocaleString()}
            </td>
            <td>
              <Link to={`/sensors/${alert.sensor_id}`}>
                Подробнее
              </Link>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default AlertsList;