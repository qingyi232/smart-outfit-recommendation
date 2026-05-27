import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-outfit-service-2026-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-smart-outfit-2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
    WEATHER_API_BASE = 'https://devapi.qweather.com/v7'
    WEATHER_GEO_BASE = 'https://geoapi.qweather.com/v2'

    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, '..', 'smart_outfit.db')
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost/smart_outfit'
    )


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
