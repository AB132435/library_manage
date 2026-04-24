from flask import Blueprint, request, jsonify
from ..models import User, Role, BorrowRecord
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表，支持搜索和分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    role_id = request.args.get('role_id', type=int)
    
    query = User.query.options(joinedload(User.role))
    
    if search:
        query = query.filter(or_(
            User.username.contains(search),
            User.email.contains(search)
        ))
    
    if role_id:
        query = query.filter_by(role_id=role_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return jsonify({
        "users": [{
            "id": u.id, 
            "username": u.username, 
            "email": u.email,
            "role_id": u.role_id,
            "role_name": u.role.name if u.role else None,
            "is_active": u.is_active
        } for u in users],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取单个用户详情"""
    user = User.query.get_or_404(user_id)
    
    # 获取用户的借阅记录
    borrow_records = BorrowRecord.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "role_name": user.role.name if user.role else None,
        "is_active": user.is_active,
        "borrow_records": [{
            "id": br.id,
            "book_id": br.book_id,
            "book_title": br.book.title if br.book else None,
            "borrow_time": br.borrow_time.isoformat() if br.borrow_time else None,
            "due_time": br.due_time.isoformat() if br.due_time else None,
            "return_time": br.return_time.isoformat() if br.return_time else None,
            "status": br.status
        } for br in borrow_records]
    }), 200

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """创建新用户"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "用户名和密码不能为空"}), 400
    
    # 检查用户名是否重复
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "用户名已存在"}), 400
    
    # 检查邮箱是否重复
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "邮箱已存在"}), 400
    
    user = User(
        username=data['username'],
        email=data.get('email'),
        role_id=data.get('role_id', 2),  # 默认读者角色
        is_active=data.get('is_active', True)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"msg": "用户创建成功", "user_id": user.id}), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "没有提供更新数据"}), 400
    
    # 检查用户名是否重复（排除自身）
    if data.get('username') and data['username'] != user.username:
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            return jsonify({"msg": "用户名已存在"}), 400
    
    # 检查邮箱是否重复（排除自身）
    if data.get('email') and data['email'] != user.email:
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({"msg": "邮箱已存在"}), 400
    
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role_id = data.get('role_id', user.role_id)
    user.is_active = data.get('is_active', user.is_active)
    
    # 如果提供了新密码，则更新密码
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({"msg": "用户更新成功"}), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 检查是否有借阅记录
    borrow_records = BorrowRecord.query.filter_by(user_id=user_id, status='borrowed').first()
    if borrow_records:
        return jsonify({"msg": "该用户有未归还的图书，无法删除"}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"msg": "用户删除成功"}), 200

@users_bp.route('/<int:user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
def toggle_user_status(user_id):
    """切换用户激活状态"""
    user = User.query.get_or_404(user_id)
    
    # 不能禁用自己
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return jsonify({"msg": "不能禁用自己"}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "激活" if user.is_active else "禁用"
    return jsonify({"msg": f"用户已{status}", "is_active": user.is_active}), 200

@users_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
def reset_user_password(user_id):
    """重置用户密码（管理员操作）"""
    user = User.query.get_or_404(user_id)
    
    # 生成随机密码或使用默认密码
    default_password = "123456"  # 实际应用中应该生成随机密码并发送邮件
    user.set_password(default_password)
    
    db.session.commit()
    
    return jsonify({"msg": "密码已重置为默认密码"}), 200