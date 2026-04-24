from flask import Blueprint, request, jsonify
from ..models import AuditLog
from .. import db
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import desc, func, cast, Date

logs_bp = Blueprint('logs', __name__)


def add_log(username, module, action, detail=''):
    """添加审计日志的辅助函数"""
    try:
        log = AuditLog(
            username=username,
            module=module,
            action=action,
            detail=detail
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[AuditLog Error] {e}")


@logs_bp.route('/', methods=['GET'])
@jwt_required()
def get_logs():
    """获取审计日志列表，支持筛选和分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    username = request.args.get('username', '')
    module = request.args.get('module', '')
    action = request.args.get('action', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = AuditLog.query

    if username:
        query = query.filter(AuditLog.username.contains(username))
    if module:
        query = query.filter_by(module=module)
    if action:
        query = query.filter_by(action=action)
    if date_from:
        try:
            dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.op_time >= dt)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(AuditLog.op_time < dt)
        except ValueError:
            pass

    query = query.order_by(desc(AuditLog.op_time))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items

    return jsonify({
        "logs": [{
            "id": log.id,
            "op_time": log.op_time.isoformat() if log.op_time else None,
            "username": log.username,
            "module": log.module,
            "action": log.action,
            "detail": log.detail
        } for log in logs],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200


@logs_bp.route('/modules', methods=['GET'])
@jwt_required()
def get_log_modules():
    """获取所有日志模块列表（用于筛选下拉框）"""
    modules = db.session.query(AuditLog.module).distinct().all()
    return jsonify([m[0] for m in modules if m[0]]), 200


@logs_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_log_stats():
    """获取审计日志统计信息（用于看板）"""
    # 按模块统计
    module_stats = db.session.query(
        AuditLog.module,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.module).all()

    # 按操作类型统计
    action_stats = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).all()

    # 按日期统计（最近7天）- 使用 func.date 兼容 SQLite
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    date_stats = db.session.query(
        func.date(AuditLog.op_time).label('date'),
        func.count(AuditLog.id).label('count')
    ).filter(AuditLog.op_time >= seven_days_ago) \
     .group_by(func.date(AuditLog.op_time)) \
     .order_by(func.date(AuditLog.op_time)) \
     .all()

    # 今日操作数
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = AuditLog.query.filter(AuditLog.op_time >= today).count()

    # 总日志数
    total_count = AuditLog.query.count()

    return jsonify({
        "module_stats": [{"module": m[0], "count": m[1]} for m in module_stats],
        "action_stats": [{"action": a[0], "count": a[1]} for a in action_stats],
        "date_stats": [{"date": str(d[0]), "count": d[1]} for d in date_stats],
        "today_count": today_count,
        "total_count": total_count
    }), 200
