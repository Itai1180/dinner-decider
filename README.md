# 随机晚饭决定器后台系统

## 环境要求
- Python 3.9+
- Git

## 安装依赖
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install Django==4.2.16
```

## 本地启动
```bash
python manage.py migrate
python manage.py runserver
```

## 页面地址
- 注册页：`/register/`
- 登录页：`/login/`

## 默认管理员账号
- 用户名：`admin`
- 密码：`admin123`

## 接口约定
- 所有接口以 `/api/` 为前缀
- 统一返回结构：`{code, msg, data}`

## 主要功能
- Django 项目骨架与 SQLite 开发配置
- 三张核心表及迁移文件
- 初始化数据：默认管理员 + 10 家默认餐馆
- 公共件：统一返回包装、登录鉴权、管理员鉴权
- 账号接口：注册、登录、登出、当前用户
