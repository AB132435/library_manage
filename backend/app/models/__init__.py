from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from .. import db

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2)
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    
    role = db.relationship('Role', backref='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.Column(db.Text)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True)
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=1)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    publisher = db.relationship('Publisher', backref='books')
    category = db.relationship('Category', backref='books')

class Publisher(db.Model):
    __tablename__ = 'publishers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_time = db.Column(db.DateTime, default=datetime.utcnow)
    due_time = db.Column(db.DateTime)
    return_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    op_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    op_ip = db.Column(db.String(15), default='127.0.0.1')
    username = db.Column(db.String(80), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    detail = db.Column(db.Text)

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db():
    """创建表并插入初始数据"""
    from .. import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # 检查是否已有管理员，没有则创建
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            print(">>> 正在初始化基础数据...")
            
            # 创建角色
            r_admin = Role(name='Admin', permissions=json.dumps({"all": True}))
            r_reader = Role(name='Reader', permissions=json.dumps({"read": True}))
            r_auditor = Role(name='Auditor', permissions=json.dumps({"read": True, "audit": True}))
            db.session.add_all([r_admin, r_reader, r_auditor])
            db.session.commit()
            
            # 创建管理员账号
            admin = User(username='admin', role_id=r_admin.id, email='admin@lib.com')
            admin.set_password('admin123')
            
            # 创建读者账号
            reader = User(username='reader', role_id=r_reader.id, email='reader@lib.com')
            reader.set_password('reader123')
            
            # 创建审计员账号
            auditor = User(username='auditor', role_id=r_auditor.id, email='auditor@lib.com')
            auditor.set_password('auditor123')
            
            db.session.add_all([admin, reader, auditor])
            
            # 创建测试图书数据
            pub = Publisher(name='机械工业出版社')
            cat = Category(name='计算机技术')
            db.session.add_all([pub, cat])
            db.session.commit()
            
            book = Book(title='Python编程：从入门到实践', isbn='9787115428028', price=89.0, stock=5, publisher_id=pub.id, category_id=cat.id)
            db.session.add(book)
            
            db.session.commit()
            print(">>> 初始数据创建成功！")
            print(">>> 管理员账号：admin / admin123")
            print(">>> 读者账号：reader / reader123")
        else:
            print(">>> 数据库已存在，检查并补充缺失数据...")
            # 确保审计员角色存在
            auditor_role = Role.query.filter_by(name='Auditor').first()
            if not auditor_role:
                auditor_role = Role(name='Auditor', permissions=json.dumps({"read": True, "audit": True}))
                db.session.add(auditor_role)
                db.session.commit()
                print(">>> 已补充创建 Auditor 角色")
            # 确保审计员账号存在
            auditor = User.query.filter_by(username='auditor').first()
            if not auditor:
                auditor = User(username='auditor', role_id=auditor_role.id, email='auditor@lib.com')
                auditor.set_password('auditor123')
                db.session.add(auditor)
                db.session.commit()
                print(">>> 已补充创建审计员账号: auditor / auditor123")
            print(">>> 数据检查完成。")
