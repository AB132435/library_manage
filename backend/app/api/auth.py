from flask import Blueprint, request, jsonify
from ..models import User, Role
from .. import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "缺少用户名或密码"}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']) and user.is_active:
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "access_token": access_token,
            "user": {"id": user.id, "username": user.username, "role_id": user.role_id}
        }), 200
    return jsonify({"msg": "用户名或密码错误"}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "缺少用户名或密码"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "用户名已存在"}), 400
    
    # 默认角色为读者 (role_id=2)
    role_id = data.get('role_id', 2)
    user = User(
        username=data['username'],
        email=data.get('email'),
        role_id=role_id
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"msg": "注册成功", "user_id": user.id}), 201

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({"msg": "缺少旧密码或新密码"}), 400
    
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user or not user.check_password(data['old_password']):
        return jsonify({"msg": "旧密码错误"}), 400
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({"msg": "密码修改成功"}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({"msg": "请输入邮箱"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"msg": "该邮箱未注册"}), 404
    
    # 在实际应用中，这里应该发送重置密码邮件
    # 这里简单返回成功消息
    return jsonify({"msg": "重置密码链接已发送到您的邮箱"}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username, "role_id": user.role_id}), 200
    return jsonify({"msg": "用户不存在"}), 404