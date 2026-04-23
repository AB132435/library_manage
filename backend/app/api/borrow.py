from flask import Blueprint, request, jsonify
from ..models import BorrowRecord, Book, User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import or_, desc
from .logs import add_log

borrow_bp = Blueprint('borrow', __name__)

@borrow_bp.route('/', methods=['GET'])
@jwt_required()
def get_borrow_records():
    """获取借阅记录列表，支持搜索和分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    user_id = request.args.get('user_id', type=int)
    
    query = BorrowRecord.query
    
    if search:
        query = query.join(Book).join(User).filter(or_(
            Book.title.contains(search),
            User.username.contains(search)
        ))
    
    if status:
        query = query.filter_by(status=status)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # 按借阅时间倒序排列
    query = query.order_by(desc(BorrowRecord.borrow_time))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    return jsonify({
        "records": [{
            "id": r.id,
            "user_id": r.user_id,
            "user_name": r.user.username if r.user else None,
            "book_id": r.book_id,
            "book_title": r.book.title if r.book else None,
            "borrow_time": r.borrow_time.isoformat() if r.borrow_time else None,
            "due_time": r.due_time.isoformat() if r.due_time else None,
            "return_time": r.return_time.isoformat() if r.return_time else None,
            "status": r.status,
            "is_overdue": r.due_time and r.due_time < datetime.utcnow() and r.status == 'borrowed'
        } for r in records],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200

@borrow_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_borrows():
    """获取当前用户的借阅记录"""
    current_user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    
    query = BorrowRecord.query.filter_by(user_id=current_user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # 按借阅时间倒序排列
    query = query.order_by(desc(BorrowRecord.borrow_time))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    
    return jsonify({
        "records": [{
            "id": r.id,
            "book_id": r.book_id,
            "book_title": r.book.title if r.book else None,
            "borrow_time": r.borrow_time.isoformat() if r.borrow_time else None,
            "due_time": r.due_time.isoformat() if r.due_time else None,
            "return_time": r.return_time.isoformat() if r.return_time else None,
            "status": r.status,
            "is_overdue": r.due_time and r.due_time < datetime.utcnow() and r.status == 'borrowed'
        } for r in records],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200

@borrow_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_borrow_record(record_id):
    """获取单个借阅记录详情"""
    record = BorrowRecord.query.get_or_404(record_id)
    
    # 检查权限：用户只能查看自己的记录，管理员可以查看所有
    current_user_id = int(get_jwt_identity())
    if record.user_id != current_user_id:
        # 这里可以添加管理员权限检查
        # 暂时允许所有用户查看（实际项目中需要权限控制）
        pass
    
    return jsonify({
        "id": record.id,
        "user_id": record.user_id,
        "user_name": record.user.username if record.user else None,
        "book_id": record.book_id,
        "book_title": record.book.title if record.book else None,
        "book_isbn": record.book.isbn if record.book else None,
        "borrow_time": record.borrow_time.isoformat() if record.borrow_time else None,
        "due_time": record.due_time.isoformat() if record.due_time else None,
        "return_time": record.return_time.isoformat() if record.return_time else None,
        "status": record.status,
        "is_overdue": record.due_time and record.due_time < datetime.utcnow() and record.status == 'borrowed'
    }), 200

@borrow_bp.route('/<int:record_id>/return', methods=['POST'])
@jwt_required()
def return_book_by_record(record_id):
    """通过借阅记录ID归还图书"""
    record = BorrowRecord.query.get_or_404(record_id)
    
    # 检查记录状态
    if record.status != 'borrowed':
        return jsonify({"msg": "该图书已归还或状态异常"}), 400
    
    # 检查权限：用户只能归还自己的图书
    current_user_id = int(get_jwt_identity())
    if record.user_id != current_user_id:
        return jsonify({"msg": "只能归还自己借阅的图书"}), 403
    
    # 更新借阅记录
    record.return_time = datetime.utcnow()
    record.status = 'returned'
    
    # 增加图书库存
    book = Book.query.get(record.book_id)
    if book:
        book.stock += 1
    
    db.session.commit()

    # 记录审计日志
    user = User.query.get(current_user_id)
    book_title = book.title if book else '未知图书'
    add_log(
        username=user.username if user else str(current_user_id),
        module='borrows',
        action='归还图书',
        detail=f"归还图书: {book_title}, 记录ID: {record.id}"
    )

    return jsonify({"msg": "归还成功"}), 200

@borrow_bp.route('/<int:record_id>/renew', methods=['POST'])
@jwt_required()
def renew_book(record_id):
    """续借图书"""
    record = BorrowRecord.query.get_or_404(record_id)
    
    # 检查记录状态
    if record.status != 'borrowed':
        return jsonify({"msg": "只能续借未归还的图书"}), 400
    
    # 检查权限：用户只能续借自己的图书
    current_user_id = int(get_jwt_identity())
    if record.user_id != current_user_id:
        return jsonify({"msg": "只能续借自己借阅的图书"}), 403
    
    # 检查是否已逾期
    if record.due_time and record.due_time < datetime.utcnow():
        return jsonify({"msg": "逾期图书不能续借，请先归还"}), 400
    
    # 续借30天
    record.due_time = record.due_time + timedelta(days=30) if record.due_time else datetime.utcnow() + timedelta(days=30)
    
    db.session.commit()
    
    return jsonify({
        "msg": "续借成功",
        "new_due_time": record.due_time.isoformat() if record.due_time else None
    }), 200

@borrow_bp.route('/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_borrow_record(record_id):
    """删除借阅记录（管理员操作）"""
    record = BorrowRecord.query.get_or_404(record_id)
    
    # 检查记录状态
    if record.status == 'borrowed':
        return jsonify({"msg": "未归还的图书不能删除记录"}), 400
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({"msg": "借阅记录删除成功"}), 200

@borrow_bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_records():
    """获取逾期借阅记录"""
    current_time = datetime.utcnow()
    
    query = BorrowRecord.query.filter(
        BorrowRecord.status == 'borrowed',
        BorrowRecord.due_time < current_time
    ).order_by(BorrowRecord.due_time)
    
    records = query.all()
    
    return jsonify({
        "records": [{
            "id": r.id,
            "user_id": r.user_id,
            "user_name": r.user.username if r.user else None,
            "book_id": r.book_id,
            "book_title": r.book.title if r.book else None,
            "borrow_time": r.borrow_time.isoformat() if r.borrow_time else None,
            "due_time": r.due_time.isoformat() if r.due_time else None,
            "overdue_days": (current_time - r.due_time).days if r.due_time else 0
        } for r in records]
    }), 200