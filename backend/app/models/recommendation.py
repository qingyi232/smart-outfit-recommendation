from datetime import datetime
from app import db


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    scene = db.Column(db.String(64), default='通勤')
    date = db.Column(db.Date, nullable=False)

    temperature = db.Column(db.Float, default=0)
    humidity = db.Column(db.Integer, default=0)
    weather_text = db.Column(db.String(64), default='')

    outfit_top = db.Column(db.Integer, db.ForeignKey('clothes.id'), nullable=True)
    outfit_bottom = db.Column(db.Integer, db.ForeignKey('clothes.id'), nullable=True)
    outfit_outer = db.Column(db.Integer, db.ForeignKey('clothes.id'), nullable=True)
    outfit_shoes = db.Column(db.Integer, db.ForeignKey('clothes.id'), nullable=True)
    outfit_accessory = db.Column(db.Integer, db.ForeignKey('clothes.id'), nullable=True)

    comfort_score = db.Column(db.Float, default=0)   # 舒适度评分 0-100
    match_score = db.Column(db.Float, default=0)      # 搭配评分 0-100
    advice_text = db.Column(db.Text, default='')      # 穿衣建议文字

    algorithm_type = db.Column(db.String(32), default='decision_tree')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    top = db.relationship('Clothing', foreign_keys=[outfit_top])
    bottom = db.relationship('Clothing', foreign_keys=[outfit_bottom])
    outer = db.relationship('Clothing', foreign_keys=[outfit_outer])
    shoes = db.relationship('Clothing', foreign_keys=[outfit_shoes])
    accessory = db.relationship('Clothing', foreign_keys=[outfit_accessory])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'city': self.city,
            'scene': self.scene,
            'date': self.date.strftime('%Y-%m-%d'),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'weather_text': self.weather_text,
            'outfit': {
                'top': self.top.to_dict() if self.top else None,
                'bottom': self.bottom.to_dict() if self.bottom else None,
                'outer': self.outer.to_dict() if self.outer else None,
                'shoes': self.shoes.to_dict() if self.shoes else None,
                'accessory': self.accessory.to_dict() if self.accessory else None,
            },
            'comfort_score': self.comfort_score,
            'match_score': self.match_score,
            'advice_text': self.advice_text,
            'algorithm_type': self.algorithm_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


class UserFeedback(db.Model):
    __tablename__ = 'user_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('recommendations.id'), nullable=False)
    rating = db.Column(db.Integer, default=3)   # 1-5
    comment = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recommendation = db.relationship('Recommendation', backref='feedbacks')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommendation_id': self.recommendation_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clothing_id = db.Column(db.Integer, db.ForeignKey('clothes.id'), nullable=False)
    preference_score = db.Column(db.Float, default=3.0)  # 0-5
    wear_count = db.Column(db.Integer, default=0)
    last_worn = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clothing = db.relationship('Clothing', backref='preferences')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'clothing_id': self.clothing_id,
            'preference_score': self.preference_score,
            'wear_count': self.wear_count,
        }
