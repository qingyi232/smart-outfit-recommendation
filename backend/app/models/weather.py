from datetime import datetime
from app import db


class WeatherRecord(db.Model):
    __tablename__ = 'weather_records'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(64), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)

    temperature = db.Column(db.Float, default=0)
    feels_like = db.Column(db.Float, default=0)
    temp_min = db.Column(db.Float, default=0)
    temp_max = db.Column(db.Float, default=0)
    humidity = db.Column(db.Integer, default=0)        # 百分比
    wind_speed = db.Column(db.Float, default=0)        # km/h
    wind_direction = db.Column(db.String(20), default='')
    weather_text = db.Column(db.String(64), default='')  # 晴/多云/雨...
    weather_icon = db.Column(db.String(20), default='')
    precipitation = db.Column(db.Float, default=0)     # 降水量 mm
    pressure = db.Column(db.Float, default=0)          # 气压 hPa
    visibility = db.Column(db.Float, default=0)        # 能见度 km
    uv_index = db.Column(db.Integer, default=0)        # 紫外线指数
    aqi = db.Column(db.Integer, default=0)             # 空气质量指数
    aqi_level = db.Column(db.String(20), default='')   # 优/良/轻度...

    sunrise = db.Column(db.String(10), default='')
    sunset = db.Column(db.String(10), default='')

    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('city', 'date', name='uq_city_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'date': self.date.strftime('%Y-%m-%d'),
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'weather_text': self.weather_text,
            'weather_icon': self.weather_icon,
            'precipitation': self.precipitation,
            'pressure': self.pressure,
            'visibility': self.visibility,
            'uv_index': self.uv_index,
            'aqi': self.aqi,
            'aqi_level': self.aqi_level,
            'sunrise': self.sunrise,
            'sunset': self.sunset,
        }
