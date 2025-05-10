# server/api/routes.py

from flask import Blueprint, jsonify

# Создаем Blueprint для API
api = Blueprint('api', __name__)

@api.route('/status', methods=['GET'])
def status():
    """Эндпоинт для проверки статуса API"""
    return jsonify({
        'status': 'success',
        'message': 'API работает нормально',
        'version': 'v1'
    }), 200