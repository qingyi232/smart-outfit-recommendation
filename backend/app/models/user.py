from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(64), default='')
    avatar = db.Column(db.String(512), default='')
    gender = db.Column(db.String(10), default='unknown')  # male / female / unknown
    age = db.Column(db.Integer, default=25)
    city = db.Column(db.String(64), default='北京')
    body_type = db.Column(db.String(20), default='normal')  # cold_sensitive / normal / heat_sensitive
    role = db.Column(db.String(20), default='user')  # user / admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recommendations = db.relationship('Recommendation', backref='user', lazy='dynamic')
    feedbacks = db.relationship('UserFeedback', backref='user', lazy='dynamic')
    preferences = db.relationship('UserPreference', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar,
            'gender': self.gender,
            'age': self.age,
            'city': self.city,
            'body_type': self.body_type,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
