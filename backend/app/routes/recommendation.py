from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.recommendation import Recommendation, UserFeedback
from app.services.weather_service import get_weather
from app.services.recommendation_engine import generate_recommendation, get_scene_list, get_model_list

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/generate', methods=['POST'])
@jwt_required()
def create_recommendation():
    uid = int(get_jwt_identity())
    data = request.get_json()
    city = data.get('city', '北京')
    scene = data.get('scene', '通勤')
    model_type = data.get('model_type', 'standard')

    weather = get_weather(city)
    result = generate_recommendation(uid, city, scene, weather, model_type=model_type)

    if not result:
        return jsonify({'code': 500, 'msg': '推荐生成失败'}), 500

    result['weather'] = weather
    return jsonify({'code': 200, 'data': result})


@recommend_bp.route('/today', methods=['GET'])
@jwt_required()
def today_recommendation():
    uid = int(get_jwt_identity())
    city = request.args.get('city', '北京')
    scene = request.args.get('scene', '通勤')
    model_type = request.args.get('model_type', 'standard')

    from datetime import date
    rec = Recommendation.query.filter_by(
        user_id=uid, city=city, scene=scene, date=date.today()
    ).order_by(Recommendation.created_at.desc()).first()

    if rec and rec.algorithm_type and model_type in rec.algorithm_type:
        weather = get_weather(city)
        result = rec.to_dict()
        result['weather'] = weather
        return jsonify({'code': 200, 'data': result})

    weather = get_weather(city)
    result = generate_recommendation(uid, city, scene, weather, model_type=model_type)
    if not result:
        return jsonify({'code': 500, 'msg': '推荐生成失败'}), 500
    result['weather'] = weather
    return jsonify({'code': 200, 'data': result})


@recommend_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    uid = int(get_jwt_identity())
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    pagination = Recommendation.query.filter_by(user_id=uid)\
        .order_by(Recommendation.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }
    })


@recommend_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    uid = int(get_jwt_identity())
    data = request.get_json()

    fb = UserFeedback(
        user_id=uid,
        recommendation_id=data.get('recommendation_id'),
        rating=data.get('rating', 3),
        comment=data.get('comment', ''),
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '反馈提交成功'})


@recommend_bp.route('/scenes', methods=['GET'])
def list_scenes():
    return jsonify({'code': 200, 'data': get_scene_list()})


@recommend_bp.route('/models', methods=['GET'])
def list_models():
    return jsonify({'code': 200, 'data': get_model_list()})


@recommend_bp.route('/history/<int:rec_id>', methods=['DELETE'])
@jwt_required()
def delete_history(rec_id):
    uid = int(get_jwt_identity())
    rec = Recommendation.query.filter_by(id=rec_id, user_id=uid).first()
    if not rec:
        return jsonify({'code': 404, 'msg': '记录不存在或无权限删除'}), 404

    UserFeedback.query.filter_by(recommendation_id=rec_id).delete()
    db.session.delete(rec)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '推荐记录已删除'})
