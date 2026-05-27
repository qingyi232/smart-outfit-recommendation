from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.recommendation import Recommendation, UserFeedback, UserPreference

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    total_recs = Recommendation.query.filter_by(user_id=uid).count()
    total_feedbacks = UserFeedback.query.filter_by(user_id=uid).count()

    avg_comfort = db.session.query(
        db.func.avg(Recommendation.comfort_score)
    ).filter_by(user_id=uid).scalar() or 0

    recent = Recommendation.query.filter_by(user_id=uid)\
        .order_by(Recommendation.created_at.desc()).limit(5).all()

    return jsonify({
        'code': 200,
        'data': {
            'user': user.to_dict(),
            'stats': {
                'total_recommendations': total_recs,
                'total_feedbacks': total_feedbacks,
                'avg_comfort_score': round(float(avg_comfort), 1),
            },
            'recent_recommendations': [r.to_dict() for r in recent],
        }
    })


@user_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    uid = int(get_jwt_identity())
    prefs = UserPreference.query.filter_by(user_id=uid).all()
    return jsonify({'code': 200, 'data': [p.to_dict() for p in prefs]})


@user_bp.route('/preferences', methods=['POST'])
@jwt_required()
def update_preference():
    uid = int(get_jwt_identity())
    data = request.get_json()
    clothing_id = data.get('clothing_id')
    score = data.get('preference_score', 3.0)

    pref = UserPreference.query.filter_by(
        user_id=uid, clothing_id=clothing_id
    ).first()

    if pref:
        pref.preference_score = score
        pref.wear_count += 1
    else:
        pref = UserPreference(
            user_id=uid,
            clothing_id=clothing_id,
            preference_score=score,
            wear_count=1,
        )
        db.session.add(pref)

    db.session.commit()
    return jsonify({'code': 200, 'msg': '偏好已更新'})
