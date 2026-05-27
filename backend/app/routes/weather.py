from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.weather_service import (
    get_weather, get_forecast, get_all_cities, calculate_comfort_index
)

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/now', methods=['GET'])
@jwt_required()
def get_current_weather():
    city = request.args.get('city', '北京')
    data = get_weather(city)
    comfort = calculate_comfort_index(
        data['temperature'], data['humidity'], data['wind_speed']
    )
    data['comfort'] = comfort
    return jsonify({'code': 200, 'data': data})


@weather_bp.route('/forecast', methods=['GET'])
@jwt_required()
def get_weather_forecast():
    city = request.args.get('city', '北京')
    days = min(int(request.args.get('days', 7)), 15)
    data = get_forecast(city, days)
    return jsonify({'code': 200, 'data': data})


@weather_bp.route('/cities', methods=['GET'])
def list_cities():
    return jsonify({'code': 200, 'data': get_all_cities()})


@weather_bp.route('/comfort', methods=['GET'])
@jwt_required()
def get_comfort():
    temp = float(request.args.get('temp', 20))
    humidity = float(request.args.get('humidity', 50))
    wind = float(request.args.get('wind', 5))
    data = calculate_comfort_index(temp, humidity, wind)
    return jsonify({'code': 200, 'data': data})
