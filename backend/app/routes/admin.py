from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from app import db
from app.models.user import User
from app.models.clothing import Clothing, ClothingCategory
from app.models.recommendation import Recommendation, UserFeedback
from app.models.weather import WeatherRecord

admin_bp = Blueprint('admin', __name__)


def require_admin(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = int(get_jwt_identity())
        user = User.query.get(uid)
        if not user or user.role != 'admin':
            return jsonify({'code': 403, 'msg': '无管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_clothes = Clothing.query.count()
    total_recs = Recommendation.query.count()
    total_feedbacks = UserFeedback.query.count()

    avg_rating = db.session.query(
        db.func.avg(UserFeedback.rating)
    ).scalar() or 0

    avg_comfort = db.session.query(
        db.func.avg(Recommendation.comfort_score)
    ).scalar() or 0

    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = User.query.filter(User.created_at >= week_ago).count()
    week_recs = Recommendation.query.filter(Recommendation.created_at >= week_ago).count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_feedbacks = UserFeedback.query.order_by(
        UserFeedback.created_at.desc()
    ).limit(10).all()

    scene_stats = db.session.query(
        Recommendation.scene, db.func.count(Recommendation.id)
    ).group_by(Recommendation.scene).all()

    city_stats = db.session.query(
        Recommendation.city, db.func.count(Recommendation.id)
    ).group_by(Recommendation.city).order_by(
        db.func.count(Recommendation.id).desc()
    ).limit(10).all()

    return jsonify({
        'code': 200,
        'data': {
            'overview': {
                'total_users': total_users,
                'total_clothes': total_clothes,
                'total_recommendations': total_recs,
                'total_feedbacks': total_feedbacks,
                'avg_rating': round(float(avg_rating), 1),
                'avg_comfort': round(float(avg_comfort), 1),
                'new_users_week': new_users,
                'week_recommendations': week_recs,
            },
            'recent_users': [u.to_dict() for u in recent_users],
            'recent_feedbacks': [{
                **f.to_dict(),
                'recommendation': f.recommendation.to_dict() if f.recommendation else None
            } for f in recent_feedbacks],
            'scene_stats': [{'scene': s, 'count': c} for s, c in scene_stats],
            'city_stats': [{'city': c, 'count': n} for c, n in city_stats],
        }
    })


@admin_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    keyword = request.args.get('keyword', '')

    query = User.query
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | (User.email.contains(keyword))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'code': 200,
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }
    })


@admin_bp.route('/users/<int:uid>/toggle', methods=['PUT'])
@require_admin
def toggle_user(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'code': 200, 'msg': '操作成功', 'data': user.to_dict()})


@admin_bp.route('/clothing', methods=['GET'])
@require_admin
def list_clothing():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    category_id = request.args.get('category_id')

    query = Clothing.query
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    pagination = query.order_by(Clothing.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'code': 200,
        'data': {
            'items': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }
    })


@admin_bp.route('/clothing', methods=['POST'])
@require_admin
def add_clothing():
    data = request.get_json()
    item = Clothing(
        name=data['name'],
        category_id=data['category_id'],
        image_url=data.get('image_url', ''),
        description=data.get('description', ''),
        warmth_level=data.get('warmth_level', 3),
        breathability=data.get('breathability', 3),
        waterproof=data.get('waterproof', 1),
        formality=data.get('formality', 3),
        min_temp=data.get('min_temp', -10),
        max_temp=data.get('max_temp', 40),
        suitable_scenes=data.get('suitable_scenes', '通勤'),
        suitable_gender=data.get('suitable_gender', 'all'),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '添加成功', 'data': item.to_dict()})


@admin_bp.route('/clothing/<int:cid>', methods=['PUT'])
@require_admin
def update_clothing(cid):
    item = Clothing.query.get(cid)
    if not item:
        return jsonify({'code': 404, 'msg': '未找到该服装'}), 404

    data = request.get_json()
    for field in ('name', 'category_id', 'image_url', 'description',
                  'warmth_level', 'breathability', 'waterproof', 'formality',
                  'min_temp', 'max_temp', 'suitable_scenes', 'suitable_gender', 'is_active'):
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': item.to_dict()})


@admin_bp.route('/clothing/<int:cid>', methods=['DELETE'])
@require_admin
def delete_clothing(cid):
    item = Clothing.query.get(cid)
    if not item:
        return jsonify({'code': 404, 'msg': '未找到该服装'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})


@admin_bp.route('/weather/records', methods=['GET'])
@require_admin
def weather_records():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    city = request.args.get('city')

    query = WeatherRecord.query
    if city:
        query = query.filter_by(city=city)

    pagination = query.order_by(WeatherRecord.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'code': 200,
        'data': {
            'items': [w.to_dict() for w in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }
    })


@admin_bp.route('/recommendations', methods=['GET'])
@require_admin
def list_recommendations():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    pagination = Recommendation.query.order_by(
        Recommendation.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for r in pagination.items:
        rd = r.to_dict()
        rd['username'] = r.user.username if r.user else ''
        items.append(rd)

    return jsonify({
        'code': 200,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }
    })


@admin_bp.route('/stats/trend', methods=['GET'])
@require_admin
def stats_trend():
    """获取最近N天的推荐趋势数据（用于推荐趋势图表）"""
    days = min(int(request.args.get('days', 30)), 90)
    today = datetime.utcnow().date()

    trend = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        start = datetime.combine(d, datetime.min.time())
        end = start + timedelta(days=1)

        rec_count = Recommendation.query.filter(
            Recommendation.created_at >= start,
            Recommendation.created_at < end
        ).count()

        fb_count = UserFeedback.query.filter(
            UserFeedback.created_at >= start,
            UserFeedback.created_at < end
        ).count()

        avg_comfort = db.session.query(
            db.func.avg(Recommendation.comfort_score)
        ).filter(
            Recommendation.created_at >= start,
            Recommendation.created_at < end
        ).scalar() or 0

        trend.append({
            'date': d.strftime('%Y-%m-%d'),
            'recommendations': rec_count,
            'feedbacks': fb_count,
            'avg_comfort': round(float(avg_comfort), 1),
        })

    return jsonify({'code': 200, 'data': trend})


@admin_bp.route('/stats/user-activity', methods=['GET'])
@require_admin
def stats_user_activity():
    """用户活跃度统计：按用户聚合推荐次数、反馈次数、平均舒适度"""
    top_n = min(int(request.args.get('top', 10)), 50)

    activity = db.session.query(
        User.id, User.username, User.nickname, User.city,
        db.func.count(Recommendation.id).label('rec_count'),
        db.func.avg(Recommendation.comfort_score).label('avg_comfort'),
    ).outerjoin(Recommendation, Recommendation.user_id == User.id)\
     .filter(User.role == 'user')\
     .group_by(User.id)\
     .order_by(db.func.count(Recommendation.id).desc())\
     .limit(top_n).all()

    fb_counts = dict(db.session.query(
        UserFeedback.user_id, db.func.count(UserFeedback.id)
    ).group_by(UserFeedback.user_id).all())

    result = []
    for uid, uname, nick, city, rec_count, avg_comfort in activity:
        result.append({
            'user_id': uid,
            'username': uname,
            'nickname': nick or uname,
            'city': city,
            'recommendation_count': int(rec_count or 0),
            'feedback_count': int(fb_counts.get(uid, 0)),
            'avg_comfort_score': round(float(avg_comfort or 0), 1),
        })

    active_today = Recommendation.query.filter(
        Recommendation.created_at >= datetime.combine(datetime.utcnow().date(), datetime.min.time())
    ).distinct(Recommendation.user_id).count()

    return jsonify({
        'code': 200,
        'data': {
            'top_users': result,
            'active_users_today': active_today,
            'total_active_users': User.query.filter_by(is_active=True, role='user').count(),
        }
    })
