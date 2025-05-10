// client/src/services/api.js
import axios from 'axios';

// Базовый URL для API - УДАЛЯЕМ ПРЕФИКС отсюда, так как он будет добавлен прокси
const API_BASE_URL = '';
const GEO_API_URL = `${API_BASE_URL}/geo`;

// Создаем экземпляр axios с базовым URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API для работы с зданиями
export const buildingsApi = {
  // Получить все здания
  getAll: () => api.get(`/api/v1/geo/buildings`),
  
  // Получить информацию о конкретном здании
  getById: (buildingId) => api.get(`/api/v1/geo/buildings/${buildingId}`),
};

// API для работы с датчиками
export const sensorsApi = {
  // Получить все датчики
  getAll: (buildingId = null) => {
    const params = buildingId ? { building_id: buildingId } : {};
    return api.get(`/api/v1/geo/sensors`, { params });
  },
  
  // Получить информацию о конкретном датчике
  getById: (sensorId) => api.get(`/api/v1/geo/sensors/${sensorId}`),
  
  // Получить показания датчика
  getReadings: (sensorId, hours = 24) => 
    api.get(`/api/v1/geo/sensors/${sensorId}/readings`, { 
      params: { hours } 
    }),
  
  // Получить предсказания для датчика
  getPredictions: (sensorId, hours = 24) => 
    api.get(`/api/v1/geo/sensors/${sensorId}/predictions`, { 
      params: { hours } 
    }),
  
  // Добавить новое показание датчика (для тестирования)
  addReading: (sensorId, value, unit) => 
    api.post(`/api/v1/geo/sensors/${sensorId}/readings`, { 
      value, unit 
    }),
};

// API для работы с тревогами
export const alertsApi = {
  // Получить все тревоги
  getAll: (hours = 24) => api.get(`/api/v1/geo/alerts`, { 
    params: { hours } 
  }),
};

// API для инициализации тестовых данных
export const utilsApi = {
  initSampleData: () => api.get('/init-sample-data'),
};

export default {
  buildings: buildingsApi,
  sensors: sensorsApi,
  alerts: alertsApi,
  utils: utilsApi,
};