from flask import Blueprint, request, jsonify
from ..models import Book, Publisher, Category, BorrowRecord, User
from .. import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import or_
from .logs import add_log

books_bp = Blueprint('books', __name__)

@books_bp.route('/', methods=['GET'])
@jwt_required()
def get_books():
    """获取图书列表，支持搜索和分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    publisher_id = request.args.get('publisher_id', type=int)
    
    query = Book.query
    
    if search:
        query = query.filter(or_(
            Book.title.contains(search),
            Book.isbn.contains(search)
        ))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if publisher_id:
        query = query.filter_by(publisher_id=publisher_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items
    
    return jsonify({
        "books": [{
            "id": b.id, "title": b.title, "isbn": b.isbn, 
            "price": b.price, "stock": b.stock,
            "publisher": b.publisher.name if b.publisher else None,
            "category": b.category.name if b.category else None
        } for b in books],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200

@books_bp.route('/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    """获取单本图书详情"""
    book = Book.query.get_or_404(book_id)
    return jsonify({
        "id": book.id, "title": book.title, "isbn": book.isbn, 
        "price": book.price, "stock": book.stock,
        "publisher": book.publisher.name if book.publisher else None,
        "category": book.category.name if book.category else None
    }), 200

@books_bp.route('/', methods=['POST'])
@jwt_required()
def create_book():
    """创建新图书"""
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({"msg": "图书标题不能为空"}), 400
    
    # 检查ISBN是否重复
    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({"msg": "ISBN已存在"}), 400
    
    book = Book(
        title=data['title'],
        isbn=data.get('isbn'),
        price=data.get('price', 0.0),
        stock=data.get('stock', 1),
        publisher_id=data.get('publisher_id'),
        category_id=data.get('category_id')
    )
    
    db.session.add(book)
    db.session.commit()

    # 记录审计日志
    add_log(
        username='system',
        module='books',
        action='新增图书',
        detail=f"新增图书: {book.title}, ISBN: {book.isbn}"
    )

    return jsonify({"msg": "图书创建成功", "book_id": book.id}), 201

@books_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    """更新图书信息"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "没有提供更新数据"}), 400
    
    # 检查ISBN是否重复（排除自身）
    if data.get('isbn') and data['isbn'] != book.isbn:
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({"msg": "ISBN已存在"}), 400
    
    book.title = data.get('title', book.title)
    book.isbn = data.get('isbn', book.isbn)
    book.price = data.get('price', book.price)
    book.stock = data.get('stock', book.stock)
    book.publisher_id = data.get('publisher_id', book.publisher_id)
    book.category_id = data.get('category_id', book.category_id)
    
    db.session.commit()

    # 记录审计日志
    add_log(
        username='system',
        module='books',
        action='编辑图书',
        detail=f"编辑图书 ID={book_id}: {book.title}, ISBN: {book.isbn}"
    )

    return jsonify({"msg": "图书更新成功"}), 200

@books_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """删除图书"""
    book = Book.query.get_or_404(book_id)
    
    # 检查是否有借阅记录
    borrow_records = BorrowRecord.query.filter_by(book_id=book_id, status='borrowed').first()
    if borrow_records:
        return jsonify({"msg": "该图书有未归还的记录，无法删除"}), 400
    
    db.session.delete(book)
    db.session.commit()

    # 记录审计日志
    add_log(
        username='system',
        module='books',
        action='删除图书',
        detail=f"删除图书 ID={book_id}: {book.title}"
    )

    return jsonify({"msg": "图书删除成功"}), 200

@books_bp.route('/<int:book_id>/borrow', methods=['POST'])
@jwt_required()
def borrow_book(book_id):
    """借阅图书"""
    book = Book.query.get_or_404(book_id)
    current_user_id = int(get_jwt_identity())
    
    # 检查库存
    if book.stock <= 0:
        return jsonify({"msg": "图书库存不足"}), 400
    
    # 检查用户是否已借阅该书且未归还
    existing_borrow = BorrowRecord.query.filter_by(
        user_id=current_user_id, 
        book_id=book_id,
        status='borrowed'
    ).first()
    
    if existing_borrow:
        return jsonify({"msg": "您已借阅该书且未归还"}), 400
    
    # 创建借阅记录
    borrow_record = BorrowRecord(
        user_id=current_user_id,
        book_id=book_id,
        borrow_time=datetime.utcnow(),
        due_time=datetime.utcnow() + timedelta(days=30),  # 借期30天
        status='borrowed'
    )
    
    # 减少库存
    book.stock -= 1
    
    db.session.add(borrow_record)
    db.session.commit()

    # 记录审计日志
    user = User.query.get(current_user_id)
    add_log(
        username=user.username if user else str(current_user_id),
        module='borrows',
        action='借阅图书',
        detail=f"借阅图书: {book.title}"
    )

    return jsonify({"msg": "借阅成功", "record_id": borrow_record.id}), 200

@books_bp.route('/<int:book_id>/return', methods=['POST'])
@jwt_required()
def return_book(book_id):
    """归还图书"""
    current_user_id = int(get_jwt_identity())
    
    # 查找用户的借阅记录
    borrow_record = BorrowRecord.query.filter_by(
        user_id=current_user_id,
        book_id=book_id,
        status='borrowed'
    ).first()
    
    if not borrow_record:
        return jsonify({"msg": "未找到该书的借阅记录"}), 404
    
    # 更新借阅记录
    borrow_record.return_time = datetime.utcnow()
    borrow_record.status = 'returned'
    
    # 增加库存
    book = Book.query.get(book_id)
    book.stock += 1
    
    db.session.commit()
    
    return jsonify({"msg": "归还成功"}), 200

@books_bp.route('/<int:book_id>/collect', methods=['POST'])
@jwt_required()
def collect_book(book_id):
    """收藏图书（简化版，实际可能需要收藏表）"""
    # 这里简单返回成功，实际项目中需要创建收藏表
    return jsonify({"msg": "收藏成功"}), 200