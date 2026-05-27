"""
天气数据采集服务 —— 数据采集层核心
支持和风天气API，并提供基于真实气象模型的本地数据生成（确保无API key时系统可用）
"""
import math
import random
from datetime import datetime, date, timedelta

import requests
from flask import current_app

from app import db
from app.models.weather import WeatherRecord

CITY_COORDS = {
    '北京': (39.90, 116.41), '上海': (31.23, 121.47), '广州': (23.13, 113.26),
    '深圳': (22.54, 114.06), '成都': (30.57, 104.07), '杭州': (30.27, 120.15),
    '武汉': (30.59, 114.31), '南京': (32.06, 118.80), '重庆': (29.56, 106.55),
    '西安': (34.26, 108.94), '长沙': (28.23, 112.94), '天津': (39.13, 117.20),
    '苏州': (31.30, 120.62), '郑州': (34.75, 113.65), '青岛': (36.07, 120.38),
    '大连': (38.91, 121.60), '哈尔滨': (45.75, 126.65), '沈阳': (41.80, 123.43),
    '昆明': (25.04, 102.71), '厦门': (24.48, 118.09), '合肥': (31.82, 117.23),
    '济南': (36.65, 117.00), '福州': (26.07, 119.30), '南昌': (28.68, 115.86),
    '太原': (37.87, 112.55), '贵阳': (26.65, 106.63), '兰州': (36.06, 103.83),
    '海口': (20.04, 110.35), '银川': (38.49, 106.23), '拉萨': (29.65, 91.13),
    '乌鲁木齐': (43.83, 87.62), '呼和浩特': (40.84, 111.75),
}

WEATHER_TYPES = [
    {'text': '晴', 'icon': '100', 'precip': 0},
    {'text': '多云', 'icon': '101', 'precip': 0},
    {'text': '阴', 'icon': '104', 'precip': 0},
    {'text': '小雨', 'icon': '305', 'precip': 5},
    {'text': '中雨', 'icon': '306', 'precip': 15},
    {'text': '大雨', 'icon': '307', 'precip': 35},
    {'text': '雷阵雨', 'icon': '302', 'precip': 20},
    {'text': '小雪', 'icon': '400', 'precip': 3},
    {'text': '中雪', 'icon': '401', 'precip': 8},
    {'text': '雨夹雪', 'icon': '404', 'precip': 6},
    {'text': '雾', 'icon': '501', 'precip': 0},
]

WIND_DIRS = ['北风', '东北风', '东风', '东南风', '南风', '西南风', '西风', '西北风']

CITY_CLIMATE = {
    '北京': {'base': 12, 'amp': 18, 'humid': 50, 'rain_prob': 0.15},
    '上海': {'base': 16, 'amp': 13, 'humid': 70, 'rain_prob': 0.30},
    '广州': {'base': 22, 'amp': 9, 'humid': 78, 'rain_prob': 0.35},
    '深圳': {'base': 23, 'amp': 8, 'humid': 76, 'rain_prob': 0.30},
    '成都': {'base': 16, 'amp': 11, 'humid': 80, 'rain_prob': 0.28},
    '杭州': {'base': 16, 'amp': 14, 'humid': 72, 'rain_prob': 0.32},
    '武汉': {'base': 16, 'amp': 16, 'humid': 75, 'rain_prob': 0.25},
    '南京': {'base': 15, 'amp': 15, 'humid': 72, 'rain_prob': 0.27},
    '重庆': {'base': 18, 'amp': 12, 'humid': 80, 'rain_prob': 0.25},
    '哈尔滨': {'base': 4, 'amp': 24, 'humid': 58, 'rain_prob': 0.18},
    '昆明': {'base': 16, 'amp': 6, 'humid': 68, 'rain_prob': 0.22},
    '海口': {'base': 25, 'amp': 6, 'humid': 82, 'rain_prob': 0.35},
    '拉萨': {'base': 8, 'amp': 13, 'humid': 35, 'rain_prob': 0.12},
    '乌鲁木齐': {'base': 7, 'amp': 22, 'humid': 45, 'rain_prob': 0.10},
}


def _get_seasonal_temp(city, target_date):
    """基于正弦气候模型计算城市在指定日期的温度"""
    climate = CITY_CLIMATE.get(city, {'base': 15, 'amp': 14, 'humid': 65, 'rain_prob': 0.20})
    day_of_year = target_date.timetuple().tm_yday
    seasonal = climate['amp'] * math.sin(2 * math.pi * (day_of_year - 80) / 365)
    daily_var = random.gauss(0, 2.5)
    return round(climate['base'] + seasonal + daily_var, 1)


def _generate_weather_for_city(city, target_date):
    """基于气候模型生成指定城市和日期的天气数据"""
    climate = CITY_CLIMATE.get(city, {'base': 15, 'amp': 14, 'humid': 65, 'rain_prob': 0.20})
    temp = _get_seasonal_temp(city, target_date)
    temp_min = round(temp - random.uniform(2, 5), 1)
    temp_max = round(temp + random.uniform(2, 5), 1)
    humidity = max(10, min(100, int(climate['humid'] + random.gauss(0, 10))))
    wind_speed = round(max(0, random.gauss(12, 8)), 1)

    is_rain = random.random() < climate['rain_prob']
    if temp < -2 and is_rain:
        wtype = random.choice([w for w in WEATHER_TYPES if '雪' in w['text']])
    elif is_rain:
        wtype = random.choice([w for w in WEATHER_TYPES if '雨' in w['text']])
    elif humidity > 85:
        wtype = next((w for w in WEATHER_TYPES if w['text'] == '雾'), WEATHER_TYPES[1])
    else:
        wtype = random.choice(WEATHER_TYPES[:3])

    wind_chill = 13.12 + 0.6215 * temp - 11.37 * (wind_speed ** 0.16) + 0.3965 * temp * (wind_speed ** 0.16)
    feels_like = round(wind_chill if temp < 10 and wind_speed > 4.8 else temp - (100 - humidity) * 0.02, 1)

    aqi = max(10, int(random.gauss(65, 35)))
    if aqi <= 50:
        aqi_level = '优'
    elif aqi <= 100:
        aqi_level = '良'
    elif aqi <= 150:
        aqi_level = '轻度污染'
    elif aqi <= 200:
        aqi_level = '中度污染'
    else:
        aqi_level = '重度污染'

    day_of_year = target_date.timetuple().tm_yday
    lat = CITY_COORDS.get(city, (35, 115))[0]
    sunrise_h = int(6 + 1.5 * math.cos(2 * math.pi * (day_of_year - 172) / 365) + (lat - 30) * 0.03)
    sunset_h = int(18 - 1.5 * math.cos(2 * math.pi * (day_of_year - 172) / 365) - (lat - 30) * 0.03)

    return {
        'city': city,
        'date': target_date,
        'temperature': temp,
        'feels_like': feels_like,
        'temp_min': temp_min,
        'temp_max': temp_max,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'wind_direction': random.choice(WIND_DIRS),
        'weather_text': wtype['text'],
        'weather_icon': wtype['icon'],
        'precipitation': round(wtype['precip'] * random.uniform(0.3, 1.5), 1) if wtype['precip'] > 0 else 0,
        'pressure': round(random.gauss(1013, 10), 1),
        'visibility': round(max(1, random.gauss(15, 5)), 1),
        'uv_index': max(0, min(12, int(random.gauss(5, 3)))) if '晴' in wtype['text'] else max(0, int(random.gauss(2, 1))),
        'aqi': aqi,
        'aqi_level': aqi_level,
        'sunrise': f'{sunrise_h:02d}:{random.randint(0, 59):02d}',
        'sunset': f'{sunset_h:02d}:{random.randint(0, 59):02d}',
    }


def _fetch_from_qweather(city, api_key):
    """尝试从和风天气API获取实时天气"""
    try:
        coords = CITY_COORDS.get(city)
        if not coords:
            return None
        location = f'{coords[1]},{coords[0]}'

        resp = requests.get(
            f'https://devapi.qweather.com/v7/weather/now',
            params={'location': location, 'key': api_key},
            timeout=5
        )
        data = resp.json()
        if data.get('code') != '200':
            return None

        now = data['now']
        return {
            'temperature': float(now.get('temp', 0)),
            'feels_like': float(now.get('feelsLike', 0)),
            'humidity': int(now.get('humidity', 0)),
            'wind_speed': float(now.get('windSpeed', 0)),
            'wind_direction': now.get('windDir', ''),
            'weather_text': now.get('text', ''),
            'weather_icon': now.get('icon', ''),
            'pressure': float(now.get('pressure', 0)),
            'visibility': float(now.get('vis', 0)),
        }
    except Exception:
        return None


def get_weather(city, target_date=None):
    """获取指定城市的天气数据（核心接口）"""
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    cached = WeatherRecord.query.filter_by(city=city, date=target_date).first()
    if cached and (datetime.utcnow() - cached.fetched_at).total_seconds() < 3600:
        return cached.to_dict()

    api_key = current_app.config.get('WEATHER_API_KEY', '')
    api_data = None
    if api_key and target_date == date.today():
        api_data = _fetch_from_qweather(city, api_key)

    weather_data = _generate_weather_for_city(city, target_date)
    if api_data:
        weather_data.update(api_data)

    try:
        if cached:
            for k, v in weather_data.items():
                if k not in ('city', 'date'):
                    setattr(cached, k, v)
            cached.fetched_at = datetime.utcnow()
        else:
            cached = WeatherRecord(**weather_data)
            db.session.add(cached)
        db.session.commit()
    except Exception:
        db.session.rollback()
        cached = WeatherRecord.query.filter_by(city=city, date=target_date).first()
        if not cached:
            weather_data.pop('city', None)
            weather_data.pop('date', None)
            return {'city': city, 'date': target_date.strftime('%Y-%m-%d'), **weather_data}

    return cached.to_dict()


def get_forecast(city, days=7):
    """获取未来N天天气预报"""
    today = date.today()
    forecast = []
    for i in range(days):
        target = today + timedelta(days=i)
        forecast.append(get_weather(city, target))
    return forecast


def get_all_cities():
    """返回支持的城市列表"""
    return list(CITY_COORDS.keys())


def calculate_comfort_index(temp, humidity, wind_speed):
    """计算人体舒适度指数（温湿指数THI）"""
    thi = (1.8 * temp + 32) - 0.55 * (1 - humidity / 100) * (1.8 * temp - 26)

    if thi < 40:
        level, desc = 1, '极冷，注意严密防寒'
    elif thi < 45:
        level, desc = 2, '寒冷，需厚实保暖衣物'
    elif thi < 55:
        level, desc = 3, '偏冷，适当增添衣物'
    elif thi < 60:
        level, desc = 4, '凉爽，适宜外出'
    elif thi < 70:
        level, desc = 5, '舒适，穿着轻便即可'
    elif thi < 75:
        level, desc = 6, '温暖，注意防晒'
    elif thi < 80:
        level, desc = 7, '偏热，穿着清凉衣物'
    else:
        level, desc = 8, '炎热，注意防暑降温'

    wind_factor = max(0, wind_speed - 10) * 0.5
    return {
        'thi': round(thi, 1),
        'level': level,
        'description': desc,
        'wind_chill_factor': round(wind_factor, 1),
    }
