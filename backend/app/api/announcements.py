from flask import Blueprint, request, jsonify
from ..models import Announcement
from .. import db
from flask_jwt_extended import jwt_required
from sqlalchemy import desc

announcements_bp = Blueprint('announcements', __name__)


@announcements_bp.route('/', methods=['GET'])
@jwt_required()
def get_announcements():
    """获取公告列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Announcement.query.order_by(desc(Announcement.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items

    return jsonify({
        "announcements": [{
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200


@announcements_bp.route('/', methods=['POST'])
@jwt_required()
def create_announcement():
    """创建公告"""
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({"msg": "公告标题不能为空"}), 400

    announcement = Announcement(
        title=data['title'],
        content=data.get('content', '')
    )
    db.session.add(announcement)
    db.session.commit()

    return jsonify({"msg": "公告创建成功", "id": announcement.id}), 201


@announcements_bp.route('/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(announcement_id):
    """删除公告"""
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    return jsonify({"msg": "公告删除成功"}), 200
