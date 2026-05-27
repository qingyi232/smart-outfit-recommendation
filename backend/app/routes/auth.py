from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'code': 400, 'msg': '请填写完整信息'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'msg': '邮箱已被注册'}), 400

    user = User(
        username=username,
        email=email,
        nickname=data.get('nickname', username),
        gender=data.get('gender', 'unknown'),
        age=data.get('age', 25),
        city=data.get('city', '北京'),
        body_type=data.get('body_type', 'normal'),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'code': 200,
        'msg': '注册成功',
        'data': {'token': token, 'user': user.to_dict()}
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

    if not user.is_active:
        return jsonify({'code': 403, 'msg': '账号已被禁用'}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {'token': token, 'user': user.to_dict()}
    })


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    return jsonify({'code': 200, 'data': user.to_dict()})


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    data = request.get_json()
    for field in ('nickname', 'avatar', 'gender', 'age', 'city', 'body_type'):
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': user.to_dict()})


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    data = request.get_json() or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'code': 400, 'msg': '请填写完整的旧密码和新密码'}), 400

    if len(new_password) < 6:
        return jsonify({'code': 400, 'msg': '新密码长度需不少于6位'}), 400

    if not user.check_password(old_password):
        return jsonify({'code': 400, 'msg': '旧密码错误'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '密码修改成功'})
