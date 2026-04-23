from flask import Blueprint, request, jsonify
from ..models import Role, User
from .. import db
from flask_jwt_extended import jwt_required
import json

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/', methods=['GET'])
@jwt_required()
def get_roles():
    """获取角色列表"""
    roles = Role.query.all()
    
    return jsonify([{
        "id": r.id,
        "name": r.name,
        "permissions": json.loads(r.permissions) if r.permissions else {},
        "user_count": User.query.filter_by(role_id=r.id).count()
    } for r in roles]), 200

@roles_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """获取单个角色详情"""
    role = Role.query.get_or_404(role_id)
    
    # 获取该角色的用户
    users = User.query.filter_by(role_id=role_id).all()
    
    return jsonify({
        "id": role.id,
        "name": role.name,
        "permissions": json.loads(role.permissions) if role.permissions else {},
        "users": [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_active": u.is_active
        } for u in users]
    }), 200

@roles_bp.route('/', methods=['POST'])
@jwt_required()
def create_role():
    """创建新角色"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"msg": "角色名称不能为空"}), 400
    
    # 检查角色名是否重复
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({"msg": "角色名称已存在"}), 400
    
    # 处理权限数据
    permissions = data.get('permissions', {})
    
    role = Role(
        name=data['name'],
        permissions=json.dumps(permissions) if permissions else None
    )
    
    db.session.add(role)
    db.session.commit()
    
    return jsonify({"msg": "角色创建成功", "role_id": role.id}), 201

@roles_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """更新角色信息"""
    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "没有提供更新数据"}), 400
    
    # 检查角色名是否重复（排除自身）
    if data.get('name') and data['name'] != role.name:
        existing = Role.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({"msg": "角色名称已存在"}), 400
    
    role.name = data.get('name', role.name)
    
    # 更新权限
    if 'permissions' in data:
        role.permissions = json.dumps(data['permissions']) if data['permissions'] else None
    
    db.session.commit()
    
    return jsonify({"msg": "角色更新成功"}), 200

@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """删除角色"""
    role = Role.query.get_or_404(role_id)
    
    # 检查是否有用户使用该角色
    user_count = User.query.filter_by(role_id=role_id).count()
    if user_count > 0:
        return jsonify({"msg": f"该角色有{user_count}个用户在使用，无法删除"}), 400
    
    # 不能删除默认角色（Admin和Reader）
    if role.name in ['Admin', 'Reader']:
        return jsonify({"msg": "系统默认角色不能删除"}), 400
    
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({"msg": "角色删除成功"}), 200

@roles_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permission_options():
    """获取权限选项列表"""
    # 定义可用的权限选项
    permission_options = {
        "dashboard": ["view", "manage"],
        "books": ["view", "add", "edit", "delete", "borrow"],
        "users": ["view", "add", "edit", "delete", "toggle_status", "reset_password"],
        "borrows": ["view", "manage", "return", "renew"],
        "roles": ["view", "add", "edit", "delete"],
        "announcements": ["view", "add", "edit", "delete"],
        "logs": ["view"],
        "system": ["settings", "backup"]
    }
    
    return jsonify(permission_options), 200