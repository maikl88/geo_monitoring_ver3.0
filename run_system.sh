#!/bin/bash
echo "Запуск серверной части..."
cd ~/path/to/geo-monitoring
source env/bin/activate
python -m server.app &
SERVER_PID=$!

sleep 5
echo "Инициализация тестовыми данными..."
curl http://localhost:5000/init-sample-data

echo "Запуск симулятора датчиков..."
python sensors_simulator.py --interval 1 &
SIMULATOR_PID=$!

echo "Запуск клиентской части..."
cd client
npm start &
CLIENT_PID=$!

# Корректное завершение всех процессов при нажатии Ctrl+C
function cleanup {
  echo "Завершение работы системы..."
  kill $SERVER_PID
  kill $SIMULATOR_PID
  kill $CLIENT_PID
  exit
}

trap cleanup SIGINT SIGTERM

# Ожидание завершения
wait