import os
from app import create_app, db
from app.models import init_db

# 检查Python缓存，提醒用户清除
pycache = os.path.join(os.path.dirname(__file__), 'app', '__pycache__')
if os.path.exists(pycache):
    import glob
    cache_files = glob.glob(os.path.join(pycache, '*.pyc'))
    if cache_files:
        print(f">>> 检测到 {len(cache_files)} 个 Python 缓存文件，建议清除后重启以确保代码变更生效")
        print(f">>> 可执行: find . -type d -name '__pycache__' -exec rm -rf {{}} + 2>/dev/null")

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
    
    print(f">>> Flask strict_slashes = {app.url_map.strict_slashes}")
    print(f">>> 后端服务启动: http://0.0.0.0:5000")
    print(f">>> 如果API仍返回301/401，请确保已清除 __pycache__ 并重启后端")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
