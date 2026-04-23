from flask import Blueprint, jsonify
from ..models import Book, User, BorrowRecord, Publisher, Category
from .. import db
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取仪表盘统计数据"""
    # 图书总数
    total_books = Book.query.count()
    
    # 用户总数
    total_users = User.query.count()
    
    # 活跃用户数（最近30天有借阅记录的用户）
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.session.query(func.count(func.distinct(BorrowRecord.user_id))).filter(
        BorrowRecord.borrow_time >= thirty_days_ago
    ).scalar() or 0
    
    # 当前借阅中的图书数
    borrowed_books = BorrowRecord.query.filter_by(status='borrowed').count()
    
    # 逾期图书数
    overdue_books = BorrowRecord.query.filter(
        BorrowRecord.status == 'borrowed',
        BorrowRecord.due_time < datetime.utcnow()
    ).count()
    
    # 今日新增借阅数
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_borrows = BorrowRecord.query.filter(
        BorrowRecord.borrow_time >= today_start
    ).count()
    
    # 今日归还数
    today_returns = BorrowRecord.query.filter(
        BorrowRecord.return_time >= today_start,
        BorrowRecord.status == 'returned'
    ).count()
    
    return jsonify({
        "total_books": total_books,
        "total_users": total_users,
        "active_users": active_users,
        "borrowed_books": borrowed_books,
        "overdue_books": overdue_books,
        "today_borrows": today_borrows,
        "today_returns": today_returns
    }), 200

@dashboard_bp.route('/publishers', methods=['GET'])
@jwt_required()
def get_publisher_stats():
    """获取出版社统计"""
    stats = db.session.query(
        Publisher.name,
        func.count(Book.id).label('book_count'),
        func.sum(Book.stock).label('total_stock')
    ).join(Book, Publisher.id == Book.publisher_id, isouter=True
    ).group_by(Publisher.id, Publisher.name
    ).order_by(desc('book_count')).all()
    
    return jsonify([{
        "publisher": stat.name,
        "book_count": stat.book_count or 0,
        "total_stock": stat.total_stock or 0
    } for stat in stats]), 200

@dashboard_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_category_stats():
    """获取分类统计"""
    stats = db.session.query(
        Category.name,
        func.count(Book.id).label('book_count'),
        func.sum(Book.stock).label('total_stock')
    ).join(Book, Category.id == Book.category_id, isouter=True
    ).group_by(Category.id, Category.name
    ).order_by(desc('book_count')).all()
    
    return jsonify([{
        "category": stat.name,
        "book_count": stat.book_count or 0,
        "total_stock": stat.total_stock or 0
    } for stat in stats]), 200

@dashboard_bp.route('/top-rated', methods=['GET'])
@jwt_required()
def get_top_rated():
    """获取热门图书（按借阅次数排名）"""
    # 统计每本书的借阅次数
    top_books = db.session.query(
        Book.id,
        Book.title,
        Book.isbn,
        func.count(BorrowRecord.id).label('borrow_count')
    ).join(BorrowRecord, Book.id == BorrowRecord.book_id, isouter=True
    ).group_by(Book.id, Book.title, Book.isbn
    ).order_by(desc('borrow_count')).limit(10).all()
    
    return jsonify([{
        "id": book.id,
        "title": book.title,
        "isbn": book.isbn,
        "borrow_count": book.borrow_count or 0
    } for book in top_books]), 200

@dashboard_bp.route('/status', methods=['GET'])
@jwt_required()
def get_status_stats():
    """获取借阅状态统计"""
    # 按状态统计借阅记录
    status_stats = db.session.query(
        BorrowRecord.status,
        func.count(BorrowRecord.id).label('count')
    ).group_by(BorrowRecord.status).all()
    
    # 按月份统计借阅趋势（最近12个月）
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    
    monthly_stats = db.session.query(
        func.strftime('%Y-%m', BorrowRecord.borrow_time).label('month'),
        func.count(BorrowRecord.id).label('count')
    ).filter(
        BorrowRecord.borrow_time >= twelve_months_ago
    ).group_by('month'
    ).order_by('month').all()
    
    # 用户活跃度统计（按借阅次数分组）
    user_activity = db.session.query(
        BorrowRecord.user_id,
        User.username,
        func.count(BorrowRecord.id).label('borrow_count')
    ).join(User, BorrowRecord.user_id == User.id
    ).group_by(BorrowRecord.user_id, User.username
    ).order_by(desc('borrow_count')).limit(10).all()
    
    return jsonify({
        "status_stats": [{
            "status": stat.status,
            "count": stat.count
        } for stat in status_stats],
        "monthly_trend": [{
            "month": stat.month,
            "count": stat.count
        } for stat in monthly_stats],
        "user_activity": [{
            "user_id": activity.user_id,
            "username": activity.username,
            "borrow_count": activity.borrow_count
        } for activity in user_activity]
    }), 200

@dashboard_bp.route('/recent-activities', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """获取最近活动"""
    recent_borrows = BorrowRecord.query.order_by(
        desc(BorrowRecord.borrow_time)
    ).limit(10).all()
    
    return jsonify([{
        "id": record.id,
        "user_name": record.user.username if record.user else None,
        "book_title": record.book.title if record.book else None,
        "action": "借阅" if record.status == 'borrowed' else "归还",
        "time": record.borrow_time.isoformat() if record.borrow_time else None,
        "status": record.status
    } for record in recent_borrows]), 200