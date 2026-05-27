"""初始化数据库并填充示例数据"""
import os
import sys
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User
from app.models.clothing import Clothing, ClothingCategory
from app.models.weather import WeatherRecord
from app.models.recommendation import Recommendation, UserFeedback, UserPreference


def init():
    app = create_app('development')
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_categories()
        seed_clothing()
        seed_users()
        seed_preferences()
        seed_weather()
        seed_recommendations()
        print('数据库初始化完成！')


def seed_categories():
    categories = [
        ('上衣', '短袖T恤、衬衫、Polo衫等', 'shirt', 1),
        ('卫衣', '圆领卫衣、连帽卫衣等', 'sweater', 2),
        ('毛衣', '针织衫、毛衣等', 'knit', 3),
        ('外套', '夹克、风衣、西装外套等', 'jacket', 4),
        ('羽绒服', '轻薄羽绒、厚羽绒服等', 'down', 5),
        ('大衣', '毛呢大衣、长款大衣等', 'coat', 6),
        ('裤子', '休闲裤、西裤、工装裤等', 'pants', 7),
        ('牛仔裤', '直筒、修身、阔腿牛仔等', 'jeans', 8),
        ('短裤', '运动短裤、休闲短裤等', 'shorts', 9),
        ('裙子', '半身裙、连衣裙等', 'skirt', 10),
        ('运动鞋', '跑步鞋、板鞋、休闲运动鞋', 'sneakers', 11),
        ('皮鞋', '商务皮鞋、乐福鞋等', 'leather', 12),
        ('靴子', '马丁靴、雪地靴、短靴等', 'boots', 13),
        ('凉鞋', '凉鞋、拖鞋等', 'sandals', 14),
        ('围巾', '羊毛围巾、丝巾等', 'scarf', 15),
        ('帽子', '棒球帽、针织帽、遮阳帽等', 'hat', 16),
        ('手套', '保暖手套、皮手套等', 'gloves', 17),
        ('太阳镜', '偏光镜、墨镜等', 'sunglasses', 18),
        ('雨伞', '折叠伞、长柄伞等', 'umbrella', 19),
    ]
    for name, desc, icon, order in categories:
        db.session.add(ClothingCategory(name=name, description=desc, icon=icon, sort_order=order))
    db.session.commit()
    print(f'  创建 {len(categories)} 个服装分类')


IMG_BASE = 'https://images.unsplash.com/photo-'

CLOTHING_DATA = [
    # (name, cat_name, img_suffix, desc, warmth, breath, water, formal, min_t, max_t, scenes, gender)
    ('纯棉圆领T恤', '上衣', '1521572163474-6864f9cf17ab?w=400', '透气舒适的纯棉面料', 1, 5, 1, 2, 18, 38, '通勤,运动,居家,旅行', 'all'),
    ('条纹Polo衫', '上衣', '1586363104862-73a885a6a8b4?w=400', '经典条纹设计Polo衫', 1, 4, 1, 3, 20, 35, '通勤,聚会,旅行', 'all'),
    ('亚麻短袖衬衫', '上衣', '1596755094514-5c72d18cea25?w=400', '天然亚麻材质清爽透气', 1, 5, 1, 3, 22, 38, '通勤,约会,旅行', 'all'),
    ('商务修身衬衫', '上衣', '1620012253295-c15cc3e65df4?w=400', '商务正装白色修身衬衫', 2, 3, 1, 5, 15, 32, '通勤,商务,约会', 'male'),
    ('雪纺碎花上衣', '上衣', '1564257631407-4d99084f7c1e?w=400', '轻盈雪纺碎花设计', 1, 5, 1, 3, 20, 36, '约会,聚会,旅行', 'female'),
    ('速干运动T恤', '上衣', '1556906781-9348cec2f8a5?w=400', '专业速干面料运动上衣', 1, 5, 1, 1, 15, 38, '运动,旅行', 'all'),

    ('圆领纯色卫衣', '卫衣', '1556821840-3a63f95609a7?w=400', '简约百搭纯色卫衣', 3, 3, 1, 2, 8, 22, '通勤,居家,旅行', 'all'),
    ('连帽加绒卫衣', '卫衣', '1578587018452-c7e6a3e4a0f4?w=400', '加绒内里保暖连帽款', 4, 2, 1, 1, 2, 18, '通勤,运动,居家', 'all'),
    ('字母印花卫衣', '卫衣', '1515886657613-9f3515b0c78f?w=400', '时尚字母印花设计', 3, 3, 1, 2, 8, 22, '通勤,聚会,旅行', 'all'),

    ('高领羊毛衫', '毛衣', '1576566588028-4147f3842f27?w=400', '100%美利奴羊毛高领款', 4, 2, 1, 4, 0, 15, '通勤,商务,约会', 'all'),
    ('圆领麻花毛衣', '毛衣', '1583743814966-8936f5b7be1a?w=400', '经典麻花纹路圆领毛衣', 4, 2, 1, 3, 2, 18, '通勤,聚会,约会', 'all'),
    ('开衫薄款针织衫', '毛衣', '1434389677669-e08b4cac3105?w=400', '薄款开衫适合初秋', 2, 4, 1, 3, 12, 25, '通勤,约会,居家', 'female'),

    ('休闲飞行夹克', '外套', '1591047139829-d91aecb6caea?w=400', 'MA-1经典飞行员夹克', 3, 3, 2, 2, 5, 20, '通勤,旅行,聚会', 'all'),
    ('英伦风衣', '外套', '1544022613-e87b8b995528?w=400', '中长款经典英伦风衣', 3, 3, 3, 4, 5, 20, '通勤,商务,约会', 'all'),
    ('牛仔外套', '外套', '1576995853123-5a10305d93c0?w=400', '经典蓝色水洗牛仔外套', 2, 3, 1, 2, 10, 25, '通勤,旅行,聚会', 'all'),
    ('西装外套', '外套', '1507679799987-c73779587ccf?w=400', '修身剪裁商务西装外套', 3, 2, 1, 5, 8, 25, '商务,约会,聚会', 'male'),
    ('防风冲锋衣', '外套', '1547036967-23d11aacaee0?w=400', '户外防风防水冲锋衣', 3, 3, 5, 1, 0, 20, '运动,旅行', 'all'),

    ('轻薄羽绒服', '羽绒服', '1548883354-7622d5bbeed9?w=400', '90白鹅绒轻薄可收纳', 4, 2, 3, 2, -5, 10, '通勤,旅行', 'all'),
    ('中长款羽绒服', '羽绒服', '1610652492-ee9260f26237?w=400', '中长款保暖羽绒服', 5, 1, 3, 2, -15, 5, '通勤,旅行', 'all'),

    ('羊毛呢大衣', '大衣', '1539533113208-f6df8cc8b543?w=400', '双面羊毛中长款大衣', 4, 2, 2, 4, -5, 12, '通勤,商务,约会', 'all'),
    ('赫本风黑色大衣', '大衣', '1548624149-3714f2c4bde2?w=400', '经典赫本风中长款', 4, 2, 2, 5, -5, 12, '通勤,约会,聚会', 'female'),

    ('休闲直筒裤', '裤子', '1542272604-fe1b457f8bdd?w=400', '宽松直筒休闲长裤', 3, 3, 1, 3, 5, 30, '通勤,旅行,居家', 'all'),
    ('工装束脚裤', '裤子', '1517438476312-10d79c077509?w=400', '多口袋工装束脚裤', 3, 3, 1, 1, 5, 28, '通勤,运动,旅行', 'all'),
    ('西裤', '裤子', '1594938298603-c8148c4dae35?w=400', '商务修身西裤', 3, 2, 1, 5, 5, 32, '商务,通勤,约会', 'male'),
    ('加绒加厚长裤', '裤子', '1605518216938-7c31b7b14ad0?w=400', '冬季加绒保暖长裤', 5, 1, 1, 2, -15, 10, '通勤,居家', 'all'),

    ('经典直筒牛仔裤', '牛仔裤', '1541099649-f3b55d2459b8?w=400', '经典蓝色直筒牛仔', 3, 3, 1, 3, 5, 30, '通勤,旅行,聚会', 'all'),
    ('修身小脚牛仔裤', '牛仔裤', '1475178626620-a4d074967571?w=400', '弹力修身小脚牛仔裤', 3, 3, 1, 3, 5, 30, '通勤,约会,聚会', 'all'),

    ('运动短裤', '短裤', '1562157873-818bc0726f68?w=400', '轻薄速干运动短裤', 1, 5, 1, 1, 22, 40, '运动,居家,旅行', 'all'),
    ('休闲五分裤', '短裤', '1591195853828-11db59a44f6b?w=400', '棉麻休闲五分短裤', 1, 5, 1, 2, 24, 40, '通勤,旅行,聚会', 'all'),

    ('A字半身裙', '裙子', '1583496661160-fb5886a773b9?w=400', '高腰A字半身裙', 2, 4, 1, 4, 15, 32, '通勤,约会,聚会', 'female'),
    ('碎花连衣裙', '裙子', '1572804013309-59a2b41e6f44?w=400', '清新碎花连衣裙', 1, 5, 1, 3, 20, 35, '约会,聚会,旅行', 'female'),

    ('经典白色板鞋', '运动鞋', '1525966222134-fcfa99b8ae77?w=400', '百搭小白鞋板鞋', 2, 4, 1, 2, 5, 35, '通勤,旅行,聚会', 'all'),
    ('专业跑步鞋', '运动鞋', '1542291026-7eec264c27ff?w=400', '缓震透气跑步运动鞋', 2, 5, 2, 1, 5, 38, '运动,旅行', 'all'),

    ('商务牛津皮鞋', '皮鞋', '1614252235316-8c857d38b5f4?w=400', '正装牛津款商务皮鞋', 2, 2, 2, 5, 5, 30, '商务,通勤,约会', 'male'),
    ('乐福鞋', '皮鞋', '1582897085600-2e6eb0410e71?w=400', '一脚蹬休闲乐福鞋', 2, 3, 1, 3, 10, 30, '通勤,约会,聚会', 'all'),

    ('经典马丁靴', '靴子', '1608256246136-7e0a3a09dcf4?w=400', '6孔经典马丁靴', 3, 2, 3, 2, -5, 18, '通勤,旅行,聚会', 'all'),
    ('保暖雪地靴', '靴子', '1610398752800-bab34eecb2a4?w=400', '加绒保暖雪地靴', 5, 1, 3, 1, -20, 5, '通勤,旅行', 'all'),

    ('清凉凉鞋', '凉鞋', '1603487742131-4160ec999306?w=400', '夏季透气休闲凉鞋', 1, 5, 1, 1, 25, 40, '通勤,旅行,居家', 'all'),

    ('羊绒围巾', '围巾', '1601924921557-45ea5cc32b84?w=400', '柔软保暖羊绒围巾', 5, 1, 1, 4, -15, 10, '通勤,商务,约会', 'all'),
    ('丝巾', '围巾', '1590874103328-4b03a8a570d4?w=400', '真丝印花方巾', 1, 5, 1, 4, 10, 30, '约会,聚会,商务', 'female'),

    ('针织毛线帽', '帽子', '1576871337622-98d48d1cf531?w=400', '冬季保暖针织帽', 5, 2, 1, 1, -15, 8, '通勤,运动,旅行', 'all'),
    ('遮阳棒球帽', '帽子', '1588850561407-ed78c334e67a?w=400', '户外遮阳棒球帽', 1, 5, 1, 1, 15, 40, '运动,旅行', 'all'),

    ('触屏保暖手套', '手套', '1545594861-3bef73feca35?w=400', '触屏功能冬季保暖手套', 5, 1, 2, 2, -20, 5, '通勤,运动,旅行', 'all'),

    ('偏光太阳镜', '太阳镜', '1511499767150-a48a237f0083?w=400', '防紫外线偏光太阳镜', 1, 5, 1, 3, 10, 40, '通勤,运动,旅行,约会', 'all'),

    ('三折自动晴雨伞', '雨伞', '1534361960057-19889db9621e?w=400', '一键开合自动折叠伞', 1, 5, 5, 3, -5, 40, '通勤,商务,旅行', 'all'),
]


def seed_clothing():
    cat_map = {c.name: c.id for c in ClothingCategory.query.all()}
    for (name, cat, img, desc, warm, breath, water, formal,
         min_t, max_t, scenes, gender) in CLOTHING_DATA:
        db.session.add(Clothing(
            name=name, category_id=cat_map[cat],
            image_url=f'{IMG_BASE}{img}',
            description=desc, warmth_level=warm, breathability=breath,
            waterproof=water, formality=formal,
            min_temp=min_t, max_temp=max_t,
            suitable_scenes=scenes, suitable_gender=gender,
        ))
    db.session.commit()
    print(f'  创建 {len(CLOTHING_DATA)} 件服装数据')


def seed_users():
    users = [
        ('admin', 'admin@smartoutfit.com', 'admin123', '系统管理员', 'male', 30, '北京', 'normal', 'admin'),
        ('zhangsan', 'zhangsan@example.com', '123456', '张三', 'male', 28, '北京', 'normal', 'user'),
        ('lisi', 'lisi@example.com', '123456', '李四', 'female', 25, '上海', 'cold_sensitive', 'user'),
        ('wangwu', 'wangwu@example.com', '123456', '王五', 'male', 35, '广州', 'heat_sensitive', 'user'),
        ('zhaoliu', 'zhaoliu@example.com', '123456', '赵六', 'female', 22, '成都', 'normal', 'user'),
        ('sunqi', 'sunqi@example.com', '123456', '孙七', 'male', 45, '杭州', 'cold_sensitive', 'user'),
        ('zhouba', 'zhouba@example.com', '123456', '周八', 'female', 60, '哈尔滨', 'cold_sensitive', 'user'),
        ('wujiu', 'wujiu@example.com', '123456', '吴九', 'male', 20, '深圳', 'heat_sensitive', 'user'),
    ]
    for uname, email, pwd, nick, gender, age, city, body, role in users:
        u = User(username=uname, email=email, nickname=nick,
                 gender=gender, age=age, city=city, body_type=body, role=role)
        u.set_password(pwd)
        db.session.add(u)
    db.session.commit()
    print(f'  创建 {len(users)} 个用户（管理员: admin/admin123，普通用户: zhangsan/123456）')


def seed_preferences():
    users = User.query.filter_by(role='user').all()
    clothes = Clothing.query.all()
    count = 0
    for u in users:
        sample = random.sample(clothes, min(15, len(clothes)))
        for c in sample:
            db.session.add(UserPreference(
                user_id=u.id, clothing_id=c.id,
                preference_score=round(random.uniform(2.0, 5.0), 1),
                wear_count=random.randint(0, 20),
            ))
            count += 1
    db.session.commit()
    print(f'  创建 {count} 条用户偏好数据')


def seed_weather():
    cities = ['北京', '上海', '广州', '成都', '杭州', '哈尔滨', '深圳']
    today = date.today()
    count = 0
    for city in cities:
        for i in range(-7, 8):
            d = today + timedelta(days=i)
            from app.services.weather_service import _generate_weather_for_city
            data = _generate_weather_for_city(city, d)
            db.session.add(WeatherRecord(**data))
            count += 1
    db.session.commit()
    print(f'  创建 {count} 条天气数据')


def seed_recommendations():
    users = User.query.filter_by(role='user').all()
    scenes = ['通勤', '运动', '约会', '旅行', '商务']
    clothes = Clothing.query.all()
    if not clothes:
        return

    tops = [c for c in clothes if c.category.name in ('上衣', '卫衣', '毛衣')]
    bottoms = [c for c in clothes if c.category.name in ('裤子', '牛仔裤', '短裤', '裙子')]
    outers = [c for c in clothes if c.category.name in ('外套', '羽绒服', '大衣')]
    shoes_list = [c for c in clothes if c.category.name in ('运动鞋', '皮鞋', '靴子', '凉鞋')]
    accessories = [c for c in clothes if c.category.name in ('围巾', '帽子', '手套', '太阳镜', '雨伞')]

    count = 0
    for u in users:
        for i in range(random.randint(5, 12)):
            d = date.today() - timedelta(days=random.randint(0, 30))
            scene = random.choice(scenes)
            temp = random.uniform(-5, 35)

            rec = Recommendation(
                user_id=u.id, city=u.city, scene=scene, date=d,
                temperature=round(temp, 1),
                humidity=random.randint(30, 90),
                weather_text=random.choice(['晴', '多云', '阴', '小雨']),
                outfit_top=random.choice(tops).id if tops else None,
                outfit_bottom=random.choice(bottoms).id if bottoms else None,
                outfit_outer=random.choice(outers).id if outers and temp < 18 else None,
                outfit_shoes=random.choice(shoes_list).id if shoes_list else None,
                outfit_accessory=random.choice(accessories).id if accessories and random.random() > 0.5 else None,
                comfort_score=round(random.uniform(60, 95), 1),
                match_score=round(random.uniform(65, 98), 1),
                advice_text=f'气温{round(temp, 1)}°C，{"注意保暖" if temp < 15 else "穿着清凉即可"}',
                algorithm_type='decision_tree+collaborative_filtering',
            )
            db.session.add(rec)
            count += 1

            if random.random() > 0.4:
                db.session.flush()
                db.session.add(UserFeedback(
                    user_id=u.id,
                    recommendation_id=rec.id,
                    rating=random.randint(3, 5),
                    comment=random.choice(['很满意', '搭配不错', '挺好的', '还可以', '非常实用']),
                ))

    db.session.commit()
    print(f'  创建 {count} 条推荐记录及反馈')


if __name__ == '__main__':
    init()
