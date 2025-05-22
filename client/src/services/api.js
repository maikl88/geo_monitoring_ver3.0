// client/src/services/api.js (обновленная версия)
import axios from 'axios';

// Базовый URL для API
const API_BASE_URL = '';

// Создаем экземпляр axios с базовым URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API для работы с зданиями (без изменений)
export const buildingsApi = {
  getAll: () => api.get(`/api/v1/geo/buildings`),
  getById: (buildingId) => api.get(`/api/v1/geo/buildings/${buildingId}`),
};

// API для работы с датчиками (обновленный)
export const sensorsApi = {
  // Существующие методы
  getAll: (buildingId = null) => {
    const params = buildingId ? { building_id: buildingId } : {};
    return api.get(`/api/v1/geo/sensors`, { params });
  },
  
  getById: (sensorId) => api.get(`/api/v1/geo/sensors/${sensorId}`),
  
  getReadings: (sensorId, hours = 24) => 
    api.get(`/api/v1/geo/sensors/${sensorId}/readings`, { 
      params: { hours } 
    }),
  
  addReading: (sensorId, value, unit) => 
    api.post(`/api/v1/geo/sensors/${sensorId}/readings`, { 
      value, unit 
    }),

  // НОВЫЕ методы для аппроксимации (заменяют getPredictions)
  getApproximation: (sensorId, hours = 24, degree = null, points = 100) => {
    const params = { hours, points };
    if (degree !== null) {
      params.degree = degree;
    }
    return api.get(`/api/v1/geo/sensors/${sensorId}/approximation`, { params });
  },

  getTrend: (sensorId, hours = 24, degree = null) => {
    const params = { hours };
    if (degree !== null) {
      params.degree = degree;
    }
    return api.get(`/api/v1/geo/sensors/${sensorId}/trend`, { params });
  },

  // УДАЛЯЕМ старый метод getPredictions
  // getPredictions: (sensorId, hours = 24) => ...
};

// API для работы с тревогами (без изменений)
export const alertsApi = {
  getAll: (hours = 24) => api.get(`/api/v1/geo/alerts`, { 
    params: { hours } 
  }),
};

// API для инициализации тестовых данных (без изменений)
export const utilsApi = {
  initSampleData: () => api.get('/init-sample-data'),
};

export default {
  buildings: buildingsApi,
  sensors: sensorsApi,
  alerts: alertsApi,
  utils: utilsApi,
};