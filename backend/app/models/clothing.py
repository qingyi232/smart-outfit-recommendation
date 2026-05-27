from datetime import datetime
from app import db


class ClothingCategory(db.Model):
    __tablename__ = 'clothing_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256), default='')
    icon = db.Column(db.String(64), default='')
    sort_order = db.Column(db.Integer, default=0)

    clothes = db.relationship('Clothing', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'sort_order': self.sort_order,
        }


class Clothing(db.Model):
    __tablename__ = 'clothes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('clothing_categories.id'), nullable=False)
    image_url = db.Column(db.String(512), default='')
    description = db.Column(db.Text, default='')

    warmth_level = db.Column(db.Integer, default=3)       # 1-5 保暖指数
    breathability = db.Column(db.Integer, default=3)       # 1-5 透气指数
    waterproof = db.Column(db.Integer, default=1)          # 1-5 防水指数
    formality = db.Column(db.Integer, default=3)           # 1-5 正式度

    min_temp = db.Column(db.Float, default=-10)            # 适用最低温度
    max_temp = db.Column(db.Float, default=40)             # 适用最高温度
    suitable_scenes = db.Column(db.String(256), default='通勤')  # 逗号分隔的场景标签
    suitable_gender = db.Column(db.String(20), default='all')    # male/female/all

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'image_url': self.image_url,
            'description': self.description,
            'warmth_level': self.warmth_level,
            'breathability': self.breathability,
            'waterproof': self.waterproof,
            'formality': self.formality,
            'min_temp': self.min_temp,
            'max_temp': self.max_temp,
            'suitable_scenes': self.suitable_scenes.split(',') if self.suitable_scenes else [],
            'suitable_gender': self.suitable_gender,
            'is_active': self.is_active,
        }
