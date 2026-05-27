from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.clothing import Clothing, ClothingCategory

clothing_bp = Blueprint('clothing', __name__)


@clothing_bp.route('/categories', methods=['GET'])
def list_categories():
    cats = ClothingCategory.query.order_by(ClothingCategory.sort_order).all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in cats]})


@clothing_bp.route('/list', methods=['GET'])
def list_clothes():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category_id = request.args.get('category_id')
    scene = request.args.get('scene')

    query = Clothing.query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=int(category_id))
    if scene:
        query = query.filter(Clothing.suitable_scenes.contains(scene))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'code': 200,
        'data': {
            'items': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
        }
    })


@clothing_bp.route('/<int:cid>', methods=['GET'])
def get_clothing(cid):
    item = Clothing.query.get(cid)
    if not item:
        return jsonify({'code': 404, 'msg': '未找到该服装'}), 404
    return jsonify({'code': 200, 'data': item.to_dict()})
