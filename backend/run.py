import os
from app import create_app, db
from app.models import init_db

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    with app.app_context():
        # 创建所有不存在的表（支持新增模型时自动建表）
        db.create_all()
        # 如果是首次运行，自动初始化数据
        if not os.path.exists(os.path.join(app.root_path, 'instance', 'library.db')):
            init_db()
            print(">>> 检测到首次运行，已自动初始化数据库和测试账号。")
        else:
            # 确保基础数据存在
            init_db()
    
    app.run(host='0.0.0.0', port=5000, debug=True)