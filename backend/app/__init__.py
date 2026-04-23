from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # 基础配置
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-prod'
    
    # 使用 SQLite 以便开箱即用（绝对路径）
    basedir = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'library.db')
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://192.168.1.89:5173'])
    
    # 注册蓝图
    from .api.auth import auth_bp
    from .api.books import books_bp
    from .api.users import users_bp
    from .api.borrow import borrow_bp
    from .api.dashboard import dashboard_bp
    from .api.roles import roles_bp
    from .api.logs import logs_bp
    from .api.announcements import announcements_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(borrow_bp, url_prefix='/api/borrows')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(roles_bp, url_prefix='/api/roles')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
    
    return app