"""
智能穿衣推荐引擎 —— 数据处理与推荐引擎核心
支持三种推荐模式：标准模式、偏暖模式、偏冷模式
基于决策树进行基础穿衣方案匹配，协同过滤实现个性化优化
"""
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import date

from app import db
from app.models.clothing import Clothing, ClothingCategory
from app.models.recommendation import Recommendation, UserFeedback, UserPreference
from app.models.user import User


SCENE_LIST = ['通勤', '运动', '约会', '聚会', '旅行', '居家', '商务']

MODEL_TYPES = ['standard', 'warm', 'cool']

TRAINING_DATA = [
    # [temp, humidity, wind, precip, aqi, scene_id] -> warmth_level
    [-10, 40, 20, 0, 60, 0, 5], [-5, 50, 15, 2, 80, 0, 5],
    [0, 55, 10, 0, 50, 0, 5], [3, 60, 12, 5, 70, 0, 4],
    [5, 50, 8, 0, 45, 0, 4], [8, 55, 10, 3, 55, 0, 4],
    [10, 60, 6, 0, 40, 0, 3], [13, 65, 8, 0, 50, 0, 3],
    [15, 60, 5, 0, 35, 0, 3], [18, 55, 6, 0, 30, 0, 2],
    [20, 50, 4, 0, 25, 0, 2], [23, 60, 5, 0, 40, 0, 2],
    [25, 70, 3, 0, 45, 0, 1], [28, 75, 4, 0, 50, 0, 1],
    [30, 80, 3, 0, 60, 0, 1], [33, 85, 2, 0, 55, 0, 1],
    [35, 90, 2, 0, 70, 0, 1],
    [-5, 50, 15, 0, 60, 1, 4], [5, 55, 10, 0, 40, 1, 3],
    [15, 60, 5, 0, 30, 1, 2], [25, 70, 3, 0, 40, 1, 1],
    [10, 60, 6, 0, 35, 2, 3], [20, 55, 4, 0, 25, 2, 2],
    [28, 65, 3, 0, 30, 2, 1],
    [10, 60, 8, 5, 50, 0, 4], [15, 70, 6, 10, 45, 0, 3],
    [20, 80, 4, 15, 55, 0, 2], [25, 85, 3, 20, 60, 0, 1],
    [5, 65, 20, 5, 70, 4, 4], [15, 55, 15, 0, 30, 4, 3],
    [25, 60, 8, 0, 35, 4, 1],
    [10, 60, 5, 0, 40, 5, 2], [20, 55, 3, 0, 30, 5, 1],
    [8, 55, 8, 0, 50, 6, 4], [18, 50, 5, 0, 35, 6, 3],
    [25, 65, 3, 0, 40, 6, 2],
]

WARM_TRAINING_DATA = [
    [-10, 40, 20, 0, 60, 0, 5], [-5, 50, 15, 2, 80, 0, 5],
    [0, 55, 10, 0, 50, 0, 5], [3, 60, 12, 5, 70, 0, 5],
    [5, 50, 8, 0, 45, 0, 5], [8, 55, 10, 3, 55, 0, 4],
    [10, 60, 6, 0, 40, 0, 4], [13, 65, 8, 0, 50, 0, 4],
    [15, 60, 5, 0, 35, 0, 3], [18, 55, 6, 0, 30, 0, 3],
    [20, 50, 4, 0, 25, 0, 3], [23, 60, 5, 0, 40, 0, 2],
    [25, 70, 3, 0, 45, 0, 2], [28, 75, 4, 0, 50, 0, 2],
    [30, 80, 3, 0, 60, 0, 1], [33, 85, 2, 0, 55, 0, 1],
    [35, 90, 2, 0, 70, 0, 1],
    [-5, 50, 15, 0, 60, 1, 5], [5, 55, 10, 0, 40, 1, 4],
    [15, 60, 5, 0, 30, 1, 3], [25, 70, 3, 0, 40, 1, 2],
    [10, 60, 6, 0, 35, 2, 4], [20, 55, 4, 0, 25, 2, 3],
    [28, 65, 3, 0, 30, 2, 2],
    [10, 60, 8, 5, 50, 0, 5], [15, 70, 6, 10, 45, 0, 4],
    [20, 80, 4, 15, 55, 0, 3], [25, 85, 3, 20, 60, 0, 2],
    [5, 65, 20, 5, 70, 4, 5], [15, 55, 15, 0, 30, 4, 4],
    [25, 60, 8, 0, 35, 4, 2],
    [10, 60, 5, 0, 40, 5, 3], [20, 55, 3, 0, 30, 5, 2],
    [8, 55, 8, 0, 50, 6, 5], [18, 50, 5, 0, 35, 6, 4],
    [25, 65, 3, 0, 40, 6, 3],
]

COOL_TRAINING_DATA = [
    [-10, 40, 20, 0, 60, 0, 4], [-5, 50, 15, 2, 80, 0, 4],
    [0, 55, 10, 0, 50, 0, 4], [3, 60, 12, 5, 70, 0, 3],
    [5, 50, 8, 0, 45, 0, 3], [8, 55, 10, 3, 55, 0, 3],
    [10, 60, 6, 0, 40, 0, 2], [13, 65, 8, 0, 50, 0, 2],
    [15, 60, 5, 0, 35, 0, 2], [18, 55, 6, 0, 30, 0, 1],
    [20, 50, 4, 0, 25, 0, 1], [23, 60, 5, 0, 40, 0, 1],
    [25, 70, 3, 0, 45, 0, 1], [28, 75, 4, 0, 50, 0, 1],
    [30, 80, 3, 0, 60, 0, 1], [33, 85, 2, 0, 55, 0, 1],
    [35, 90, 2, 0, 70, 0, 1],
    [-5, 50, 15, 0, 60, 1, 3], [5, 55, 10, 0, 40, 1, 2],
    [15, 60, 5, 0, 30, 1, 1], [25, 70, 3, 0, 40, 1, 1],
    [10, 60, 6, 0, 35, 2, 2], [20, 55, 4, 0, 25, 2, 1],
    [28, 65, 3, 0, 30, 2, 1],
    [10, 60, 8, 5, 50, 0, 3], [15, 70, 6, 10, 45, 0, 2],
    [20, 80, 4, 15, 55, 0, 1], [25, 85, 3, 20, 60, 0, 1],
    [5, 65, 20, 5, 70, 4, 3], [15, 55, 15, 0, 30, 4, 2],
    [25, 60, 8, 0, 35, 4, 1],
    [10, 60, 5, 0, 40, 5, 1], [20, 55, 3, 0, 30, 5, 1],
    [8, 55, 8, 0, 50, 6, 3], [18, 50, 5, 0, 35, 6, 2],
    [25, 65, 3, 0, 40, 6, 1],
]


class DecisionTreeRecommender:
    """决策树推荐模型：根据天气参数和场景确定保暖等级"""

    def __init__(self, training_data=None, model_name='standard', max_depth=8, min_samples_split=3):
        self.model_name = model_name
        self.model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=2,
            random_state=42
        )
        self._training_data = training_data if training_data is not None else TRAINING_DATA
        self._train()

    def _train(self):
        data = np.array(self._training_data)
        X = data[:, :-1]  # temp, humidity, wind, precip, aqi, scene_id
        y = data[:, -1]   # warmth_level
        self.model.fit(X, y)

    def predict_warmth_level(self, temp, humidity, wind_speed, precipitation, aqi, scene):
        scene_id = SCENE_LIST.index(scene) if scene in SCENE_LIST else 0
        features = np.array([[temp, humidity, wind_speed, precipitation, aqi, scene_id]])
        return int(self.model.predict(features)[0])


class CollaborativeFilter:
    """协同过滤推荐：基于用户-物品偏好矩阵实现个性化推荐"""

    def get_similar_users(self, user_id, top_n=5):
        """计算用户相似度，找到最相似的N个用户"""
        all_prefs = UserPreference.query.all()
        if not all_prefs:
            return []

        user_items = {}
        for p in all_prefs:
            user_items.setdefault(p.user_id, {})[p.clothing_id] = p.preference_score

        if user_id not in user_items:
            return []

        target = user_items[user_id]
        similarities = []

        for other_id, other_prefs in user_items.items():
            if other_id == user_id:
                continue
            common = set(target.keys()) & set(other_prefs.keys())
            if len(common) < 2:
                continue

            vec_a = np.array([target[i] for i in common])
            vec_b = np.array([other_prefs[i] for i in common])

            norm_a, norm_b = np.linalg.norm(vec_a), np.linalg.norm(vec_b)
            if norm_a == 0 or norm_b == 0:
                continue
            cos_sim = np.dot(vec_a, vec_b) / (norm_a * norm_b)
            similarities.append((other_id, cos_sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    def recommend_items(self, user_id, candidate_ids, top_n=3):
        """基于相似用户对候选服装进行评分排序"""
        similar = self.get_similar_users(user_id)
        if not similar:
            return candidate_ids[:top_n]

        scores = {}
        for cid in candidate_ids:
            weighted_sum, sim_sum = 0.0, 0.0
            for other_id, sim in similar:
                pref = UserPreference.query.filter_by(
                    user_id=other_id, clothing_id=cid
                ).first()
                if pref:
                    weighted_sum += sim * pref.preference_score
                    sim_sum += abs(sim)
            scores[cid] = weighted_sum / sim_sum if sim_sum > 0 else 3.0

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [cid for cid, _ in ranked[:top_n]]


dt_standard = DecisionTreeRecommender(
    training_data=TRAINING_DATA,
    model_name='standard',
    max_depth=8,
    min_samples_split=3
)
dt_warm = DecisionTreeRecommender(
    training_data=WARM_TRAINING_DATA,
    model_name='warm',
    max_depth=6,
    min_samples_split=2
)
dt_cool = DecisionTreeRecommender(
    training_data=COOL_TRAINING_DATA,
    model_name='cool',
    max_depth=6,
    min_samples_split=2
)
cf_model = CollaborativeFilter()

DT_MODELS = {
    'standard': dt_standard,
    'warm': dt_warm,
    'cool': dt_cool,
}

MODEL_DESCRIPTIONS = {
    'standard': '标准模式 — 根据天气和场景进行均衡推荐',
    'warm': '偏暖模式 — 适合怕冷人群，推荐更保暖的穿搭方案',
    'cool': '偏冷模式 — 适合怕热人群，推荐更清凉透气的穿搭方案',
}


def generate_recommendation(user_id, city, scene, weather_data, model_type='standard'):
    """生成完整的穿衣推荐方案"""
    user = User.query.get(user_id)
    if not user:
        return None

    if model_type not in DT_MODELS:
        model_type = 'standard'

    dt_model = DT_MODELS[model_type]

    temp = weather_data.get('temperature', 20)
    humidity = weather_data.get('humidity', 50)
    wind_speed = weather_data.get('wind_speed', 5)
    precipitation = weather_data.get('precipitation', 0)
    aqi = weather_data.get('aqi', 50)

    warmth = dt_model.predict_warmth_level(temp, humidity, wind_speed, precipitation, aqi, scene)

    if user.body_type == 'cold_sensitive':
        warmth = min(5, warmth + 1)
    elif user.body_type == 'heat_sensitive':
        warmth = max(1, warmth - 1)

    if user.age and user.age > 60:
        warmth = min(5, warmth + 1)

    gender_filter = user.gender if user.gender in ('male', 'female') else 'all'

    categories = {
        'top': ['上衣', 'T恤', '衬衫', '卫衣', '毛衣', '针织衫'],
        'bottom': ['裤子', '裙子', '短裤', '牛仔裤', '西裤'],
        'outer': ['外套', '夹克', '风衣', '羽绒服', '大衣', '棉服'],
        'shoes': ['鞋子', '运动鞋', '皮鞋', '靴子', '凉鞋'],
        'accessory': ['配饰', '围巾', '帽子', '手套', '太阳镜', '雨伞'],
    }

    outfit = {}
    for slot, cat_names in categories.items():
        cats = ClothingCategory.query.filter(ClothingCategory.name.in_(cat_names)).all()
        cat_ids = [c.id for c in cats]

        query = Clothing.query.filter(
            Clothing.category_id.in_(cat_ids),
            Clothing.is_active == True,
            Clothing.min_temp <= temp,
            Clothing.max_temp >= temp,
        )

        if gender_filter != 'all':
            query = query.filter(
                (Clothing.suitable_gender == gender_filter) | (Clothing.suitable_gender == 'all')
            )

        if scene:
            query = query.filter(Clothing.suitable_scenes.contains(scene))

        warmth_diff_expr = db.func.abs(Clothing.warmth_level - warmth)
        candidates = query.order_by(warmth_diff_expr).limit(20).all()

        if not candidates:
            query_fallback = Clothing.query.filter(
                Clothing.category_id.in_(cat_ids),
                Clothing.is_active == True,
            )
            candidates = query_fallback.order_by(warmth_diff_expr).limit(10).all()

        if candidates:
            candidate_ids = [c.id for c in candidates]
            cf_ranked = cf_model.recommend_items(user_id, candidate_ids, top_n=1)
            outfit[slot] = cf_ranked[0] if cf_ranked else candidates[0].id

    need_outer = warmth >= 3 or precipitation > 0 or wind_speed > 15
    need_accessory = warmth >= 4 or precipitation > 0 or aqi > 150

    advice_parts = []
    model_label = {'standard': '标准', 'warm': '偏暖', 'cool': '偏冷'}.get(model_type, '标准')

    if warmth >= 4:
        advice_parts.append(f'[{model_label}模式] 今日气温{temp}°C，体感较冷，建议穿着保暖衣物')
    elif warmth >= 3:
        advice_parts.append(f'[{model_label}模式] 今日气温{temp}°C，温度适中偏凉，建议适当添衣')
    elif warmth >= 2:
        advice_parts.append(f'[{model_label}模式] 今日气温{temp}°C，较为舒适，穿着轻便即可')
    else:
        advice_parts.append(f'[{model_label}模式] 今日气温{temp}°C，天气炎热，注意防暑降温')

    if precipitation > 5:
        advice_parts.append('有降水，建议携带雨伞')
    if wind_speed > 15:
        advice_parts.append(f'风力较大（{wind_speed}km/h），注意防风')
    if aqi > 100:
        advice_parts.append(f'空气质量{weather_data.get("aqi_level", "一般")}，建议佩戴口罩')
    if weather_data.get('uv_index', 0) > 6:
        advice_parts.append('紫外线较强，注意防晒')

    scene_tips = {
        '运动': '运动场景建议选择透气排汗面料',
        '商务': '商务场合建议着正装',
        '约会': '约会建议选择得体有品质感的搭配',
        '旅行': '旅行建议穿着舒适便于行走的衣物和鞋子',
    }
    if scene in scene_tips:
        advice_parts.append(scene_tips[scene])

    base_comfort = 80 - abs(temp - 22) * 2 - abs(humidity - 55) * 0.3 - wind_speed * 0.5

    if model_type == 'warm':
        mode_adjust = max(-10, min(8, (20 - temp) * 0.6))
    elif model_type == 'cool':
        mode_adjust = max(-10, min(8, (temp - 20) * 0.6))
    else:
        mode_adjust = 2

    ideal_warmth_standard = dt_standard.predict_warmth_level(
        temp, humidity, wind_speed, precipitation, aqi, scene
    )
    warmth_fit = max(0, 8 - abs(warmth - ideal_warmth_standard) * 3)
    comfort = max(5, min(98, base_comfort + mode_adjust + warmth_fit))

    warmth_offset = {1: 2, 2: 4, 3: 5, 4: 3, 5: 1}.get(warmth, 3)
    match = comfort * 0.85 + warmth_offset * 2.5 + 3
    if model_type == 'warm':
        match += max(-6, min(5, (18 - temp) * 0.4))
    elif model_type == 'cool':
        match += max(-6, min(5, (temp - 22) * 0.4))
    match = max(5, min(98, match))

    algorithm_label = {
        'standard': 'decision_tree_standard+collaborative_filtering',
        'warm': 'decision_tree_warm+collaborative_filtering',
        'cool': 'decision_tree_cool+collaborative_filtering',
    }.get(model_type, 'decision_tree_standard+collaborative_filtering')

    rec = Recommendation(
        user_id=user_id,
        city=city,
        scene=scene,
        date=date.today(),
        temperature=temp,
        humidity=humidity,
        weather_text=weather_data.get('weather_text', ''),
        outfit_top=outfit.get('top'),
        outfit_bottom=outfit.get('bottom'),
        outfit_outer=outfit.get('outer') if need_outer else None,
        outfit_shoes=outfit.get('shoes'),
        outfit_accessory=outfit.get('accessory') if need_accessory else None,
        comfort_score=round(comfort, 1),
        match_score=round(match, 1),
        advice_text='；'.join(advice_parts),
        algorithm_type=algorithm_label,
    )
    db.session.add(rec)
    db.session.commit()

    return rec.to_dict()


def get_scene_list():
    return SCENE_LIST


def get_model_list():
    return [
        {'key': k, 'name': v, 'algorithm': DT_MODELS[k].model_name}
        for k, v in MODEL_DESCRIPTIONS.items()
    ]
