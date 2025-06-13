// // client/src/components/SensorDetails.js (ДОБАВЛЯЕМ АВТОПРОКРУТКУ)

// import React, { useState, useEffect, useRef } from 'react';
// import { useParams, Link } from 'react-router-dom';
// import { Container, Row, Col, Card, Alert, Button, Badge, Spinner, Form } from 'react-bootstrap';
// import { sensorsApi } from '../services/api';
// import SensorChart from './SensorChart';
// import ApproximationView from './ApproximationView';

// const SensorDetails = () => {
//   const { sensorId } = useParams();
//   const [sensor, setSensor] = useState(null);
//   const [readings, setReadings] = useState([]);
//   const [approximationData, setApproximationData] = useState(null);
//   const [trendAnalysis, setTrendAnalysis] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [timeRange, setTimeRange] = useState(24);
//   const [polynomialDegree, setPolynomialDegree] = useState('auto');
  
//   // Состояния для автообновления
//   const [autoRefresh, setAutoRefresh] = useState(false);
//   const [refreshInterval, setRefreshInterval] = useState(5);
  
//   // Состояние для автопрокрутки
//   const [autoScroll, setAutoScroll] = useState(true);
  
//   // Refs для прокрутки
//   const chartRef = useRef(null);
//   const bottomRef = useRef(null);

//   useEffect(() => {
//     fetchSensorData();
    
//     let intervalId = null;
//     if (autoRefresh) {
//       console.log(`Установка автообновления с интервалом ${refreshInterval} секунд`);
//       intervalId = setInterval(() => {
//         console.log("Автоматическое обновление данных...");
//         fetchSensorData();
//       }, refreshInterval * 1000);
//     }
    
//     return () => {
//       if (intervalId) {
//         console.log("Очистка интервала автообновления");
//         clearInterval(intervalId);
//       }
//     };
//   }, [sensorId, timeRange, polynomialDegree, autoRefresh, refreshInterval]);

//   // Автопрокрутка при обновлении данных
//   useEffect(() => {
//     if (autoScroll && !loading && (readings.length > 0 || approximationData)) {
//       // Прокручиваем к графику или в самый низ
//       if (chartRef.current) {
//         chartRef.current.scrollIntoView({ 
//           behavior: 'smooth', 
//           block: 'start' 
//         });
//       } else if (bottomRef.current) {
//         bottomRef.current.scrollIntoView({ 
//           behavior: 'smooth' 
//         });
//       }
//     }
//   }, [readings, approximationData, autoScroll, loading]);

//   const fetchSensorData = async () => {
//     try {
//       setLoading(true);
      
//       // Загружаем информацию о датчике
//       const sensorResponse = await sensorsApi.getById(sensorId);
//       setSensor(sensorResponse.data);
      
//       // Загружаем показания датчика
//       const readingsResponse = await sensorsApi.getReadings(sensorId, timeRange);
//       setReadings(readingsResponse.data);
      
//       // Загружаем аппроксимацию
//       const degree = polynomialDegree === 'auto' ? null : parseInt(polynomialDegree);
//       const approximationResponse = await sensorsApi.getApproximation(sensorId, timeRange, degree);
//       setApproximationData(approximationResponse.data.approximation_data);
//       setTrendAnalysis(approximationResponse.data.trend_analysis);
      
//       setError(null);
//     } catch (err) {
//       console.error('Ошибка загрузки данных датчика:', err);
//       setError('Не удалось загрузить данные датчика. Проверьте соединение с сервером.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleTimeRangeChange = (e) => {
//     setTimeRange(parseInt(e.target.value));
//   };

//   const handlePolynomialDegreeChange = (e) => {
//     setPolynomialDegree(e.target.value);
//   };

//   // Функция принудительной прокрутки вниз
//   const scrollToBottom = () => {
//     if (bottomRef.current) {
//       bottomRef.current.scrollIntoView({ behavior: 'smooth' });
//     }
//   };

//   // Функция прокрутки к графику
//   const scrollToChart = () => {
//     if (chartRef.current) {
//       chartRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
//     }
//   };

//   if (loading) {
//     return (
//       <Container className="text-center mt-5">
//         <Spinner animation="border" role="status">
//           <span className="visually-hidden">Загрузка...</span>
//         </Spinner>
//         <p className="mt-2">Загрузка данных датчика...</p>
//       </Container>
//     );
//   }

//   if (error) {
//     return (
//       <Container className="mt-5">
//         <Alert variant="danger">
//           <Alert.Heading>Ошибка</Alert.Heading>
//           <p>{error}</p>
//           <div className="d-flex justify-content-end">
//             <Link to="/">
//               <Button variant="outline-danger">Вернуться на дашборд</Button>
//             </Link>
//           </div>
//         </Alert>
//       </Container>
//     );
//   }

//   if (!sensor) {
//     return (
//       <Container className="mt-5">
//         <Alert variant="warning">
//           <Alert.Heading>Датчик не найден</Alert.Heading>
//           <p>Датчик с ID {sensorId} не найден.</p>
//           <div className="d-flex justify-content-end">
//             <Link to="/">
//               <Button variant="outline-primary">Вернуться на дашборд</Button>
//             </Link>
//           </div>
//         </Alert>
//       </Container>
//     );
//   }

//   // Определяем единицу измерения
//   const unit = sensor.last_reading ? sensor.last_reading.unit : '';

//   return (
//     <Container fluid>
//       <div className="d-flex align-items-center mb-4">
//         <Link to={`/buildings/${sensor.building_id}`} className="me-3">
//           <Button variant="outline-secondary" size="sm">← Назад к зданию</Button>
//         </Link>
//         <h1 className="mb-0">{sensor.name}</h1>
//       </div>

//       <Row className="mb-4">
//         <Col lg={8}>
//           <Card className="sensor-details-card">
//             <Card.Header as="h5">Информация о датчике</Card.Header>
//             <Card.Body>
//               <Row>
//                 <Col md={6}>
//                   <p><strong>Тип:</strong> {sensor.type}</p>
//                   <p><strong>Расположение:</strong> {sensor.location}</p>
//                   <p><strong>Этаж:</strong> {sensor.floor || 'Не указан'}</p>
//                 </Col>
//                 <Col md={6}>
//                   <p><strong>Статус:</strong> 
//                     <Badge bg={sensor.status === 'active' ? 'success' : 'warning'} className="ms-2">
//                       {sensor.status === 'active' ? 'Активен' : 'Обслуживание'}
//                     </Badge>
//                   </p>
//                   {sensor.last_reading && (
//                     <>
//                       <p><strong>Последнее показание:</strong> {sensor.last_reading.value} {sensor.last_reading.unit}</p>
//                       <p><strong>Время последнего показания:</strong> {new Date(sensor.last_reading.timestamp).toLocaleString()}</p>
//                     </>
//                   )}
//                 </Col>
//               </Row>
//             </Card.Body>
//           </Card>
//         </Col>

//         <Col lg={4}>
//           <Card className="sensor-details-card">
//             <Card.Header as="h5">Настройки анализа</Card.Header>
//             <Card.Body>
//               <Form>
//                 <Form.Group className="mb-3">
//                   <Form.Label>Период анализа данных</Form.Label>
//                   <Form.Select value={timeRange} onChange={handleTimeRangeChange}>
//                     <option value="1">За последний час</option>
//                     <option value="6">Последние 6 часов</option>
//                     <option value="12">Последние 12 часов</option>
//                     <option value="24">Последние 24 часа</option>
//                     <option value="48">Последние 2 дня</option>
//                     <option value="72">Последние 3 дня</option>
//                     <option value="168">Последняя неделя</option>
//                   </Form.Select>
//                 </Form.Group>

//                 <Form.Group className="mb-3">
//                   <Form.Label>Степень полинома для аппроксимации</Form.Label>
//                   <Form.Select value={polynomialDegree} onChange={handlePolynomialDegreeChange}>
//                     <option value="auto">Автоматический выбор</option>
//                     <option value="2">2 (квадратичная)</option>
//                     <option value="3">3 (кубическая)</option>
//                     <option value="4">4 (четвертой степени)</option>
//                     <option value="5">5 (пятой степени)</option>
//                   </Form.Select>
//                   <Form.Text className="text-muted">
//                     Высокие степени лучше следуют данным, но могут быть менее стабильными
//                   </Form.Text>
//                 </Form.Group>
                
//                 <Form.Group className="mb-3">
//                   <Form.Check 
//                     type="switch"
//                     id="auto-refresh-switch"
//                     label="Автоматическое обновление"
//                     checked={autoRefresh}
//                     onChange={() => setAutoRefresh(!autoRefresh)}
//                   />
//                 </Form.Group>
                
//                 {autoRefresh && (
//                   <Form.Group className="mb-3">
//                     <Form.Label>Интервал обновления (секунды)</Form.Label>
//                     <Form.Select 
//                       value={refreshInterval}
//                       onChange={(e) => setRefreshInterval(Number(e.target.value))}
//                     >
//                       <option value="1">1 секунда ⚡</option>
//                       <option value="2">2 секунды 🚀</option>
//                       <option value="5">5 секунд</option>
//                       <option value="10">10 секунд</option>
//                       <option value="30">30 секунд</option>
//                       <option value="60">1 минута</option>
//                     </Form.Select>
//                   </Form.Group>
//                 )}

//                 {/* НОВОЕ: Настройки прокрутки */}
//                 <Form.Group className="mb-3">
//                   <Form.Check 
//                     type="switch"
//                     id="auto-scroll-switch"
//                     label="Автопрокрутка к графику"
//                     checked={autoScroll}
//                     onChange={() => setAutoScroll(!autoScroll)}
//                   />
//                   <Form.Text className="text-muted">
//                     Автоматически прокручивать к графику при обновлении
//                   </Form.Text>
//                 </Form.Group>
                
//                 <div className="d-grid gap-2">
//                   <Button variant="primary" onClick={fetchSensorData}>
//                     Обновить данные сейчас
//                   </Button>
                  
//                   <Button variant="outline-secondary" onClick={scrollToChart}>
//                     📊 К графику
//                   </Button>
                  
//                   <Button variant="outline-secondary" onClick={scrollToBottom}>
//                     ⬇️ Вниз страницы
//                   </Button>
//                 </div>
//               </Form>
//             </Card.Body>
//           </Card>
//         </Col>
//       </Row>

//       {/* Блок анализа аппроксимации */}
//       <Row className="mb-4">
//         <Col>
//           <ApproximationView 
//             approximationData={approximationData} 
//             trendAnalysis={trendAnalysis}
//             unit={unit} 
//             sensorType={sensor.type}
//           />
//         </Col>
//       </Row>

//       {/* График с аппроксимацией */}
//       <Row>
//         <Col>
//           <h2 className="mb-3">График показаний с аппроксимацией</h2>
//           <div ref={chartRef}>
//             <SensorChart 
//               readings={readings} 
//               approximationData={approximationData}
//               sensorType={sensor.type}
//               unit={unit}
//             />
//           </div>
//         </Col>
//       </Row>

//       {/* Невидимый элемент в самом низу для прокрутки */}
//       <div ref={bottomRef} style={{ height: '20px', marginTop: '20px' }}></div>
//     </Container>
//   );
// };

// export default SensorDetails;

// client/src/components/SensorDetails.js (С НАЧАЛЬНОЙ ПРОКРУТКОЙ ВНИЗ)

// client/src/components/SensorDetails.js (МГНОВЕННАЯ ЗАГРУЗКА ВНИЗУ)

// client/src/components/SensorDetails.js (МГНОВЕННАЯ ЗАГРУЗКА ВНИЗУ)

import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Button, Badge, Spinner, Form } from 'react-bootstrap';
import { sensorsApi } from '../services/api';
import SensorChart from './SensorChart';
import ApproximationView from './ApproximationView';

const SensorDetails = () => {
  const { sensorId } = useParams();
  const [sensor, setSensor] = useState(null);
  const [readings, setReadings] = useState([]);
  const [approximationData, setApproximationData] = useState(null);
  const [trendAnalysis, setTrendAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(24);
  const [polynomialDegree, setPolynomialDegree] = useState('auto');
  
  // Состояния для автообновления
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5);
  
  // Состояние для автопрокрутки
  const [autoScroll, setAutoScroll] = useState(true);
  
  // ⭐ НОВОЕ: Флаг для мгновенной прокрутки
  const [shouldScrollInstantly, setShouldScrollInstantly] = useState(true);
  
  // Refs для прокрутки
  const chartRef = useRef(null);
  const bottomRef = useRef(null);

  // ⭐ ГЛАВНЫЙ useEffect - мгновенная прокрутка при загрузке
  useEffect(() => {
    if (shouldScrollInstantly && chartRef.current && !loading) {
      // МГНОВЕННАЯ прокрутка БЕЗ анимации
      chartRef.current.scrollIntoView({ 
        behavior: 'instant',  // Без анимации!
        block: 'start' 
      });
      
      // Альтернативный способ - прямая установка позиции
      const chartPosition = chartRef.current.offsetTop - 50; // 50px отступ
      window.scrollTo(0, chartPosition);
      
      console.log("📊 Мгновенная прокрутка к графику выполнена");
      setShouldScrollInstantly(false); // Отключаем после первой прокрутки
    }
  }, [shouldScrollInstantly, loading, chartRef]);

  useEffect(() => {
    fetchSensorData();
    
    let intervalId = null;
    if (autoRefresh) {
      console.log(`Установка автообновления с интервалом ${refreshInterval} секунд`);
      intervalId = setInterval(() => {
        console.log("Автоматическое обновление данных...");
        // ⭐ При автообновлении используем ту же логику что и кнопка
        handleManualRefresh();
      }, refreshInterval * 1000);
    }
    
    return () => {
      if (intervalId) {
        console.log("Очистка интервала автообновления");
        clearInterval(intervalId);
      }
    };
  }, [sensorId, timeRange, polynomialDegree, autoRefresh, refreshInterval]);

  // ⭐ ТОЛЬКО для ручного обновления - убираем этот useEffect (не нужен)
  // При автообновлении теперь используется handleManualRefresh()

  const fetchSensorData = async () => {
    try {
      setLoading(true);
      
      // Загружаем информацию о датчике
      const sensorResponse = await sensorsApi.getById(sensorId);
      setSensor(sensorResponse.data);
      
      // Загружаем показания датчика
      const readingsResponse = await sensorsApi.getReadings(sensorId, timeRange);
      setReadings(readingsResponse.data);
      
      // Загружаем аппроксимацию
      const degree = polynomialDegree === 'auto' ? null : parseInt(polynomialDegree);
      const approximationResponse = await sensorsApi.getApproximation(sensorId, timeRange, degree);
      setApproximationData(approximationResponse.data.approximation_data);
      setTrendAnalysis(approximationResponse.data.trend_analysis);
      
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

  const handlePolynomialDegreeChange = (e) => {
    setPolynomialDegree(e.target.value);
  };

  // ⭐ РУЧНОЕ обновление - с мгновенной прокруткой к графику
  const handleManualRefresh = () => {
    setShouldScrollInstantly(true); // Включаем мгновенную прокрутку
    fetchSensorData();
  };

  // Функция принудительной прокрутки вниз
  const scrollToBottom = () => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Функция прокрутки к графику
  const scrollToChart = () => {
    if (chartRef.current) {
      chartRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Функция прокрутки наверх
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ⭐ При включении автообновления - сразу к графику как кнопка
  const handleAutoRefreshToggle = () => {
    const newAutoRefresh = !autoRefresh;
    setAutoRefresh(newAutoRefresh);
    
    if (newAutoRefresh) {
      // При включении автообновления - работает как кнопка "Обновить и к графику"
      handleManualRefresh();
    }
  };

  if (loading) {
    // ⭐ Показываем спиннер в том же месте где будет график
    return (
      <>
        {/* Заполнитель для верхней части */}
        <div style={{ height: '400px' }}></div>
        
        <Container className="text-center">
          <Spinner animation="border" role="status" size="lg">
            <span className="visually-hidden">Загрузка...</span>
          </Spinner>
          <h4 className="mt-3">📊 Загрузка графика датчика...</h4>
          <p className="text-muted">
            Страница откроется на графике
          </p>
        </Container>
        
        {/* Заполнитель для нижней части */}
        <div style={{ height: '200px' }}></div>
      </>
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
        
        {/* Индикатор автообновления */}
        {autoRefresh && (
          <Badge bg="success" className="ms-3">
            🔄 Автообновление {refreshInterval}с
          </Badge>
        )}
      </div>

      <Row className="mb-4">
        <Col lg={8}>
          <Card className="sensor-details-card">
            <Card.Header as="h5">Информация о датчике</Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <p><strong>Тип:</strong> {sensor.type}</p>
                  <p><strong>Расположение:</strong> {sensor.location}</p>
                  <p><strong>Этаж:</strong> {sensor.floor || 'Не указан'}</p>
                </Col>
                <Col md={6}>
                  <p><strong>Статус:</strong> 
                    <Badge bg={sensor.status === 'active' ? 'success' : 'warning'} className="ms-2">
                      {sensor.status === 'active' ? 'Активен' : 'Обслуживание'}
                    </Badge>
                  </p>
                  {sensor.last_reading && (
                    <>
                      <p><strong>Последнее показание:</strong> {sensor.last_reading.value} {sensor.last_reading.unit}</p>
                      <p><strong>Время последнего показания:</strong> {new Date(sensor.last_reading.timestamp).toLocaleString()}</p>
                    </>
                  )}
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          <Card className="sensor-details-card">
            <Card.Header as="h5">⚡ Быстрые настройки</Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Период анализа данных</Form.Label>
                  <Form.Select value={timeRange} onChange={handleTimeRangeChange}>
                    <option value="1">За последний час</option>
                    <option value="6">Последние 6 часов</option>
                    <option value="12">Последние 12 часов</option>
                    <option value="24">Последние 24 часа</option>
                    <option value="48">Последние 2 дня</option>
                    <option value="72">Последние 3 дня</option>
                    <option value="168">Последняя неделя</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Степень полинома</Form.Label>
                  <Form.Select value={polynomialDegree} onChange={handlePolynomialDegreeChange}>
                    <option value="auto">Автоматический выбор</option>
                    <option value="2">2 (квадратичная)</option>
                    <option value="3">3 (кубическая)</option>
                    <option value="4">4 (четвертой степени)</option>
                    <option value="5">5 (пятой степени)</option>
                  </Form.Select>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Check 
                    type="switch"
                    id="auto-refresh-switch"
                    label="🔄 Автообновление графика"
                    checked={autoRefresh}
                    onChange={handleAutoRefreshToggle}
                  />
                  <Form.Text className="text-success">
                    {autoRefresh ? '✅ Каждое обновление прокручивает к графику как кнопка' : 'Включите для автоматического мониторинга'}
                  </Form.Text>
                </Form.Group>
                
                {autoRefresh && (
                  <Form.Group className="mb-3">
                    <Form.Label>Интервал обновления (секунды)</Form.Label>
                    <Form.Select 
                      value={refreshInterval}
                      onChange={(e) => setRefreshInterval(Number(e.target.value))}
                    >
                      <option value="1">1 секунда ⚡</option>
                      <option value="2">2 секунды 🚀</option>
                      <option value="5">5 секунд</option>
                      <option value="10">10 секунд</option>
                      <option value="30">30 секунд</option>
                      <option value="60">1 минута</option>
                    </Form.Select>
                  </Form.Group>
                )}
                
                <div className="d-grid gap-2">
                  <Button variant="primary" onClick={handleManualRefresh}>
                    🔄 Обновить и к графику
                  </Button>
                  
                  <Button variant="outline-info" onClick={scrollToTop}>
                    ⬆️ К информации о датчике
                  </Button>
                  
                  <Button variant="outline-secondary" onClick={scrollToChart}>
                    📊 К графику (плавно)
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Блок анализа аппроксимации */}
      <Row className="mb-4">
        <Col>
          <ApproximationView 
            approximationData={approximationData} 
            trendAnalysis={trendAnalysis}
            unit={unit} 
            sensorType={sensor.type}
          />
        </Col>
      </Row>

      {/* ⭐ ГЛАВНЫЙ БЛОК - График (сюда будет мгновенная прокрутка) */}
      <Row>
        <Col>
          <div ref={chartRef}>
            <div className="d-flex align-items-center mb-3">
              <h2 className="mb-0">📊 График показаний с аппроксимацией</h2>
              {autoRefresh && (
                <Badge bg="success" className="ms-3">
                  🔄 Обновляется каждые {refreshInterval}с
                </Badge>
              )}
            </div>
            
            <SensorChart 
              readings={readings} 
              approximationData={approximationData}
              sensorType={sensor.type}
              unit={unit}
            />
          </div>
        </Col>
      </Row>

      {/* Невидимый элемент в самом низу */}
      <div ref={bottomRef} style={{ height: '50px', marginTop: '20px' }}></div>
    </Container>
  );
};

export default SensorDetails;