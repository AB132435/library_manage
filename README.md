# 智慧图书管理系统

基于 Flask + Vue.js + MySQL 的前后端分离架构的图书管理系统，支持管理员、读者、审计员三种角色，实现图书管理、借阅归还、权限控制、审计日志、数据可视化等功能。

---

## 技术栈

### 后端
- **Flask** — Python Web 框架
- **Flask-SQLAlchemy** — ORM 数据库操作
- **Flask-JWT-Extended** — JWT 身份认证
- **Flask-CORS** — 跨域处理
- **SQLite / MySQL** — 数据存储（默认 SQLite，开箱即用）
- **Werkzeug** — 密码哈希

### 前端
- **Vue 3** — 渐进式 JavaScript 框架
- **Vite** — 构建工具
- **Element Plus** — UI 组件库
- **Axios** — HTTP 请求库
- **ECharts** — 数据可视化图表

---

## 项目结构

```
library_manage/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── __init__.py   # Flask 应用工厂
│   │   ├── api/          # API 蓝图
│   │   │   ├── auth.py       # 登录认证
│   │   │   ├── books.py      # 图书管理
│   │   │   ├── borrow.py     # 借阅管理
│   │   │   ├── users.py      # 用户管理
│   │   │   ├── logs.py       # 审计日志
│   │   │   ├── roles.py      # 角色权限
│   │   │   ├── dashboard.py  # 数据大屏
│   │   │   └── announcements.py # 公告管理
│   │   ├── models/       # 数据模型
│   │   └── instance/     # SQLite 数据库文件
│   ├── requirements.txt  # Python 依赖
│   └── run.py           # 启动入口
│
└── frontend/            # 前端应用
    ├── src/
    │   ├── api/          # API 接口封装
    │   ├── views/        # 页面组件
    │   ├── router/       # 路由配置
    │   ├── store/        # Pinia 状态管理
    │   └── App.vue       # 根组件
    ├── vite.config.js    # Vite 配置
    └── package.json      # Node 依赖
```

---

## 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

---

## 后端部署

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# 或
venv\Scripts\activate           # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包列表：
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- Flask-JWT-Extended
- Werkzeug

### 4. 启动服务

```bash
python run.py
```

服务默认运行在 `http://0.0.0.0:5000`

首次启动会自动：
- 创建 SQLite 数据库文件
- 初始化测试账号（见下方默认账号）
- 创建默认角色和图书数据

### 5. 生产环境配置（可选）

如需使用 MySQL，修改 `backend/app/__init__.py`：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/library_db'
```

---

## 前端部署

### 1. 进入前端目录

```bash
cd frontend
```

### 2. 安装依赖

```bash
npm install
# 或
yarn install
```

### 3. 开发模式启动

```bash
npm run dev
```

默认运行在 `http://localhost:5173`

开发模式下，Vite 会自动将 `/api` 请求代理到 `http://localhost:5000`

### 4. 生产构建

```bash
npm run build
```

构建产物在 `frontend/dist/` 目录，可部署到 Nginx 等静态服务器。

---

## 默认登录账号

系统首次启动会自动创建以下测试账号：

| 角色 | 用户名 | 密码 | 权限 |
|---|---|---|---|
| 管理员 | `admin` | `admin123` | 图书增删改查、用户管理、角色权限、数据大屏 |
| 读者 | `reader` | `reader123` | 图书查询、借阅、归还、查看个人借阅记录 |
| 审计员 | `auditor` | `auditor123` | 审计日志看板、操作记录查询 |

---

## 常见问题

### Q1: 前端请求返回 401 Unauthorized
**原因**：JWT Token 过期或丢失。  
**解决**：退出重新登录，或清除浏览器 LocalStorage 后刷新页面。

### Q2: 新增图书/查询图书失败，浏览器控制台报 CORS 错误
**原因**：Flask 默认 `strict_slashes=True`，URL 尾部斜杠不一致导致 301 重定向，重定向过程中 Authorization header 丢失。  
**解决**：已统一设置 `app.url_map.strict_slashes = False`，如仍有问题请清除后端 `__pycache__` 并重启：

```bash
find backend -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
python run.py
```

### Q3: 后端崩溃，报 `AttributeError: 'User' object has no attribute 'role'`
**原因**：模型关系未正确定义，或修改模型后未重新初始化数据库。  
**解决**：删除数据库文件重新初始化：

```bash
rm backend/app/instance/library.db
python run.py
```

### Q4: 前端端口不是 5173，如何配置代理
修改 `frontend/vite.config.js` 中的 `server.proxy` 配置，或修改后端 CORS 允许的来源。

---

## API 接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/books` | GET | 图书列表 |
| `/api/books` | POST | 新增图书 |
| `/api/books/<id>` | PUT | 编辑图书 |
| `/api/books/<id>` | DELETE | 删除图书 |
| `/api/books/<id>/borrow` | POST | 借阅图书 |
| `/api/borrows/my` | GET | 我的借阅记录 |
| `/api/borrows/<id>/return` | POST | 归还图书 |
| `/api/users` | GET | 用户列表 |
| `/api/logs` | GET | 审计日志 |
| `/api/logs/stats` | GET | 日志统计（看板） |
| `/api/dashboard` | GET | 数据大屏统计 |

---

## 开源协议

MIT License
