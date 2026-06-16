# 随机晚饭决定器后台系统（前后端分离）

## 架构说明
- `backend/`：Django 纯 API，负责 `/api/*`
- `frontend/`：静态 HTML/JS 页面，由 Nginx 直接返回
- `nginx/`：项目级 Nginx 配置
- `nginx-1.29.6/`：本地 Nginx 程序目录

## 环境要求
- Python 3.9+
- Git
- Nginx

## 安装依赖
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## 启动后端
```bash
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

## 启动 Nginx
```bash
cp nginx/dinner.conf.example nginx/dinner.conf
# 把 nginx/dinner.conf 里的 root 改成你本机 frontend/ 的绝对路径
# 再把该 server 配置 include 到你本机 Nginx 的 nginx.conf 的 http 块中
nginx
```

## 页面访问
- `http://127.0.0.1/login.html`
- `http://127.0.0.1/register.html`

## 默认管理员账号
- 用户名：`admin`
- 密码：`admin123`

## 接口约定
- 所有接口以 `/api/` 为前缀
- 统一返回结构：`{code, msg, data}`
- 前端请求统一使用相对路径并带 `credentials: 'same-origin'`

## Nginx 说明
- 仓库只提交 `nginx/dinner.conf.example`
- `nginx/dinner.conf` 含本机绝对路径，不进仓库
- 统一从 `http://127.0.0.1/` 访问，不要直接打开 `8000` 端口页面

## 主要功能
- Django 纯 API 骨架与 SQLite 开发配置
- 三张核心表及迁移文件
- 初始化数据：默认管理员 + 10 家默认餐馆
- 公共件：统一返回包装、登录鉴权、管理员鉴权
- 账号接口：注册、登录、登出、当前用户
- 分离式前端页面：登录、注册、首页占位
