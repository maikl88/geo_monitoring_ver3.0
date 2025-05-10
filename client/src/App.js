// client/src/App.js
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import './styles/App.css';

// Импорт компонентов
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import BuildingDetails from './components/BuildingDetails';
import SensorDetails from './components/SensorDetails';

function App() {
  return (
    <div className="app-container">
      <Header />
      <Container fluid className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/buildings/:buildingId" element={<BuildingDetails />} />
          <Route path="/sensors/:sensorId" element={<SensorDetails />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
      <footer className="footer text-center py-3 mt-auto">
        <Container>
          <span className="text-muted">© 2025 Система геотехнического мониторинга</span>
        </Container>
      </footer>
    </div>
  );
}

export default App;