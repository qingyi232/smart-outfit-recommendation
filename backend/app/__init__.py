from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .config import config_map

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map['development']))

    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'code': 401, 'msg': '登录已过期，请重新登录'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'code': 401, 'msg': '无效的令牌，请重新登录'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'code': 401, 'msg': '请先登录'}), 401

    from .routes.auth import auth_bp
    from .routes.weather import weather_bp
    from .routes.recommendation import recommend_bp
    from .routes.clothing import clothing_bp
    from .routes.admin import admin_bp
    from .routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    app.register_blueprint(clothing_bp, url_prefix='/api/clothing')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app
