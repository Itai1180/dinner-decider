# A 同学工作任务说明：账号与项目底座

> 本文档面向「随机晚饭决定器后台系统」中的 **A 同学** 模块，可由 AI 编码助手直接阅读并逐步完成全部任务。
> 阅读者请**严格按顺序执行**，每完成一步先自测通过再进入下一步。所有接口返回必须遵循本文「统一返回格式」。

---

## 0. 角色与范围

A 同学负责整个团队的**地基**，产出最先合入、供 B/C/D 三人拉取作为起步模板。

**负责内容：**

- Django 项目骨架（settings、urls、SQLite 配置、Session）
- 三张表的 `models.py` 定义与数据库迁移（建表唯一权威）
- 初始化数据（默认管理员 + 10 家默认餐馆）
- 公共件一：统一返回包装（`{code, msg, data}`）
- 公共件二：登录鉴权装饰器（需登录 / 需管理员）
- 接口 #1 注册、#2 登录、#3 登出、#11 当前用户
- 页面 `login.html`、`register.html`

**不负责（其他人做）：** 餐馆 CRUD（B）、随机抽取与历史（C）、主页大转盘/base.html/Nginx（D）。

**技术栈：** Django + 原生 JS（前后端不分离），开发期 SQLite，生产期 MySQL。

---

## 1. 全局约定（所有接口必须遵守）

### 1.1 统一返回格式

所有接口无论成功或失败，一律返回如下 JSON 结构，HTTP 状态码统一用 200，业务结果由 `code` 区分：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": { }
}
```

### 1.2 错误码表

| code | 含义 | 典型场景 |
|------|------|----------|
| 200 | 操作成功 | 所有正常返回 |
| 4000 | 参数错误 | 缺少必填字段 / 格式非法 |
| 4001 | 用户名为空或已存在 | 注册 |
| 4002 | 账号或密码错误 | 登录 |
| 4003 | 无权限（非管理员） | 餐馆增删改/启停（B 模块用） |
| 4004 | 无可用候选餐馆 | 随机抽取（C 模块用） |
| 4005 | 权重非法（需 1~100 的整数） | 新增/编辑餐馆（B 模块用） |
| 4006 | 资源不存在 | 编辑/删除/启停目标 id 不存在 |
| 4010 | 未登录 | 携带无效或缺失 Session |
| 5000 | 服务器内部错误 | 未捕获异常 |

> A 模块直接用到：200、4000、4001、4002、4010。其余码也要在统一返回工具/错误码常量中预先定义好，供 B、C 复用。

### 1.3 校验顺序规则

统一「**先格式后业务**」：先校验参数格式与必填项（不合法返回 4000），通过后再做业务校验（唯一性 4001、账号密码 4002、权限 4003 等）。

### 1.4 登录态规则

除 **#1 注册、#2 登录** 外，所有接口均需有效 Session，未登录统一返回 **4010**。

---

## 2. 任务步骤

### 步骤 1：搭建 Django 项目骨架

1. 创建项目与 app：

   ```bash
   django-admin startproject dinner .
   python manage.py startapp app
   ```

2. 在 `dinner/settings.py` 中：
   - `INSTALLED_APPS` 加入 `'app'`。
   - 数据库使用默认 SQLite（开发期），无需改动 `DATABASES`。
   - 确认 `MIDDLEWARE` 含 `django.contrib.sessions.middleware.SessionMiddleware`。
   - 模板目录：`TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']`。
   - 因前后端不分离且用原生 JS 调接口，开发期可将 `app/views.py` 中接口用 `@csrf_exempt` 豁免 CSRF（生产环境再按需收紧），或为前端注入 CSRF token。本规范开发期采用 `@csrf_exempt`。

3. 验证骨架可启动：

   ```bash
   python manage.py runserver
   ```

   能正常启动即通过。**此仓库结构需尽早推送**，供 B/C/D 拉取。

---

### 步骤 2：定义 models.py 并迁移建表

> **建表唯一权威是 Django 迁移（migrate），不要手工执行原生建表 SQL。**

在 `app/models.py` 写入三张表（字段须与下方完全对齐）：

```python
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)      # 存哈希
    nickname = models.CharField(max_length=30)
    is_admin = models.BooleanField(default=False)     # TINYINT(1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_user'


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, default='other')  # fastfood/hotpot/snack/chinese/western/other
    avg_price = models.IntegerField(default=0)        # 纯展示，不参与抽取
    weight = models.IntegerField(default=1)           # 1~100，应用层校验
    is_active = models.BooleanField(default=True)     # 启用/禁用
    is_deleted = models.BooleanField(default=False)   # 软删除标记
    draw_count = models.IntegerField(default=0)       # 累计被抽中次数
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_restaurant'


class DrawHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    restaurant = models.ForeignKey(
        Restaurant, null=True, on_delete=models.SET_NULL, db_column='restaurant_id'
    )
    restaurant_name = models.CharField(max_length=100)  # 抽中时名称快照
    drawn_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_draw_history'
```

> 说明：表名用 `db_table` 固定为 `app_user / app_restaurant / app_draw_history`，与全队接口契约一致。`avg_price` 仅展示用；`weight` 的 1~100 范围由应用层保证（B 模块校验，返回 4005）。

执行迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 步骤 3：写入初始化数据

> 用 **data migration** 或自定义管理命令写入，**不要手工 INSERT**。
> **默认管理员密码必须用 `make_password` 生成**，否则无法登录（最常见的坑）。

推荐用数据迁移。生成空迁移后填充：

```bash
python manage.py makemigrations app --empty --name seed_data
```

在生成的迁移文件中：

```python
from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed(apps, schema_editor):
    User = apps.get_model('app', 'User')
    Restaurant = apps.get_model('app', 'Restaurant')

    User.objects.create(
        username='admin',
        password=make_password('admin123'),   # 默认密码 admin123，可自行修改
        nickname='管理员',
        is_admin=True,
    )

    data = [
        ('麦当劳', 'fastfood', 35, 5),
        ('肯德基', 'fastfood', 35, 4),
        ('海底捞', 'hotpot', 120, 2),
        ('沙县小吃', 'snack', 20, 6),
        ('兰州拉面', 'snack', 25, 5),
        ('黄焖鸡米饭', 'chinese', 28, 4),
        ('必胜客', 'western', 90, 2),
        ('煲仔饭', 'chinese', 30, 3),
        ('麻辣烫', 'snack', 32, 5),
        ('日式寿司', 'western', 110, 1),
    ]
    for name, cat, price, w in data:
        Restaurant.objects.create(
            name=name, category=cat, avg_price=price,
            weight=w, is_active=True, is_deleted=False,
        )


def unseed(apps, schema_editor):
    apps.get_model('app', 'User').objects.filter(username='admin').delete()
    apps.get_model('app', 'Restaurant').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [('app', '0001_initial')]   # 改成上一条迁移的实际名称
    operations = [migrations.RunPython(seed, unseed)]
```

执行：

```bash
python manage.py migrate
```

验证：默认管理员 `admin / admin123` 存在，10 家餐馆入库。

---

### 步骤 4：统一返回包装（公共件，全队依赖）

新建 `app/common.py`：

```python
from django.http import JsonResponse

# 错误码常量（全队共用）
CODE_OK = 200
CODE_PARAM = 4000          # 参数错误
CODE_USERNAME = 4001       # 用户名为空或已存在
CODE_LOGIN_FAIL = 4002     # 账号或密码错误
CODE_FORBIDDEN = 4003      # 无权限
CODE_NO_CANDIDATE = 4004   # 无可用候选餐馆
CODE_WEIGHT = 4005         # 权重非法
CODE_NOT_FOUND = 4006      # 资源不存在
CODE_UNAUTH = 4010         # 未登录
CODE_SERVER = 5000         # 服务器内部错误

_DEFAULT_MSG = {
    200: '操作成功', 4000: '参数错误', 4001: '用户名为空或已存在',
    4002: '账号或密码错误', 4003: '无权限', 4004: '无可用候选餐馆',
    4005: '权重非法（需1~100的整数）', 4006: '资源不存在',
    4010: '未登录', 5000: '服务器内部错误',
}


def api_response(code=200, data=None, msg=None):
    """统一返回包装：{code, msg, data}，HTTP 状态码恒为 200。"""
    if msg is None:
        msg = _DEFAULT_MSG.get(code, '')
    return JsonResponse({'code': code, 'msg': msg, 'data': data})
```

> 接口签名一旦稳定，尽量不要频繁改动，因为 B、C 都会 import 它。

---

### 步骤 5：登录鉴权装饰器（公共件，全队依赖）

在 `app/common.py` 追加：

```python
from functools import wraps
from .models import User


def login_required_api(view_func):
    """需登录：无有效 Session 返回 4010。"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('user_id')
        if not uid or not User.objects.filter(id=uid).exists():
            return api_response(CODE_UNAUTH)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required_api(view_func):
    """需管理员：未登录 4010，非管理员 4003。供 B 模块写操作使用。"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('user_id')
        user = User.objects.filter(id=uid).first() if uid else None
        if user is None:
            return api_response(CODE_UNAUTH)
        if not user.is_admin:
            return api_response(CODE_FORBIDDEN)
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

### 步骤 6：实现 4 个接口

在 `app/views.py` 实现。所有接口走统一返回，遵守「先格式后业务」与登录态规则。

#### #1 `POST /api/register/` 注册

- **入参：** `{ "username", "password", "nickname" }`
- **逻辑：** 先校验格式（username 长度 1~50、password 长度 6~128、nickname 长度 1~30，任一不合法 → 4000）→ 校验 username 唯一（重复 → 4001）→ `make_password` 加密 → 建 User（is_admin 默认 0）。
- **成功返回：** `{ "user_id", "username" }`

#### #2 `POST /api/login/` 登录

- **入参：** `{ "username", "password" }`
- **逻辑：** 查用户 + `check_password` 校验（失败 → 4002）→ 写 `session["user_id"] = user.id`。
- **成功返回：** `{ "user_id", "nickname", "is_admin" }`

#### #3 `POST /api/logout/` 登出

- **入参：** 无（依赖 Session Cookie）
- **逻辑：** `request.session.flush()`，幂等，未登录也返回成功。
- **成功返回：** `null`

#### #11 `GET /api/me/` 当前登录用户信息

- **入参：** 无
- **逻辑：** 读 `session["user_id"]`，返回用户信息；未登录 → 4010（用 `@login_required_api`）。
- **成功返回：** `{ "user_id", "nickname", "is_admin" }`

参考实现：

```python
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .common import api_response, login_required_api, CODE_PARAM, CODE_USERNAME, CODE_LOGIN_FAIL
from .models import User


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except (ValueError, TypeError):
        return None


@csrf_exempt
def register(request):
    if request.method != 'POST':
        return api_response(CODE_PARAM, msg='请使用 POST')
    d = _body(request)
    if d is None:
        return api_response(CODE_PARAM, msg='请求体格式错误')
    username = (d.get('username') or '').strip()
    password = d.get('password') or ''
    nickname = (d.get('nickname') or '').strip()
    # 先格式
    if not (1 <= len(username) <= 50):
        return api_response(CODE_PARAM, msg='用户名长度需为 1~50')
    if not (6 <= len(password) <= 128):
        return api_response(CODE_PARAM, msg='密码长度需为 6~128')
    if not (1 <= len(nickname) <= 30):
        return api_response(CODE_PARAM, msg='昵称长度需为 1~30')
    # 再业务
    if User.objects.filter(username=username).exists():
        return api_response(CODE_USERNAME)
    user = User.objects.create(
        username=username, password=make_password(password),
        nickname=nickname, is_admin=False,
    )
    return api_response(data={'user_id': user.id, 'username': user.username})


@csrf_exempt
def login(request):
    if request.method != 'POST':
        return api_response(CODE_PARAM, msg='请使用 POST')
    d = _body(request)
    if d is None:
        return api_response(CODE_PARAM, msg='请求体格式错误')
    username = (d.get('username') or '').strip()
    password = d.get('password') or ''
    if not username or not password:
        return api_response(CODE_PARAM, msg='账号或密码不能为空')
    user = User.objects.filter(username=username).first()
    if user is None or not check_password(password, user.password):
        return api_response(CODE_LOGIN_FAIL)
    request.session['user_id'] = user.id
    return api_response(data={
        'user_id': user.id, 'nickname': user.nickname,
        'is_admin': 1 if user.is_admin else 0,
    })


@csrf_exempt
def logout(request):
    request.session.flush()
    return api_response(data=None)


@login_required_api
def me(request):
    user = User.objects.get(id=request.session['user_id'])
    return api_response(data={
        'user_id': user.id, 'nickname': user.nickname,
        'is_admin': 1 if user.is_admin else 0,
    })
```

#### 路由注册

在 `app/urls.py`（新建）并在 `dinner/urls.py` include：

```python
# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.register),
    path('api/login/', views.login),
    path('api/logout/', views.logout),
    path('api/me/', views.me),
]
```

```python
# dinner/urls.py
from django.urls import path, include
urlpatterns = [path('', include('app.urls'))]
```

> 注意：B 的 `/api/restaurants/...`、C 的 `/api/random-dinner/`、`/api/history/` 后续也并入 `app/urls.py`，A 先占好 4 条即可。

---

### 步骤 7：登录 / 注册页面

在 `templates/` 下创建 `register.html`、`login.html`，用原生 JS 调接口。要点：

- `fetch` 请求带 `headers: {'Content-Type': 'application/json'}`，并 `credentials: 'same-origin'` 以携带 Session Cookie。
- 先判断响应 `code === 200` 再处理 `data`，否则弹出 `msg`。
- 注册成功后引导到登录页；登录成功后跳转主页（主页 `index.html` 由 D 负责，可先跳 `/` 占位）。

`register.html` 最小示例：

```html
<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>注册</title></head>
<body>
  <h2>注册</h2>
  <input id="username" placeholder="用户名(1~50)">
  <input id="nickname" placeholder="昵称(1~30)">
  <input id="password" type="password" placeholder="密码(6~128)">
  <button onclick="doRegister()">注册</button>
  <p><a href="/login/">已有账号？去登录</a></p>
  <script>
    async function doRegister() {
      const body = {
        username: document.getElementById('username').value,
        nickname: document.getElementById('nickname').value,
        password: document.getElementById('password').value,
      };
      const r = await fetch('/api/register/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'same-origin',
        body: JSON.stringify(body),
      });
      const res = await r.json();
      if (res.code === 200) { alert('注册成功'); location.href = '/login/'; }
      else { alert(res.msg); }
    }
  </script>
</body>
</html>
```

`login.html` 同理，调 `/api/login/`，成功后 `location.href = '/'`。

为这两个页面加路由（渲染模板）：

```python
# app/urls.py 追加
from django.views.generic import TemplateView
urlpatterns += [
    path('register/', TemplateView.as_view(template_name='register.html')),
    path('login/', TemplateView.as_view(template_name='login.html')),
]
```

---

### 步骤 8：自测并最先合入

**自测清单（全部通过才算完成）：**

1. `runserver` 正常启动，无报错。
2. 打开 `/register/` 注册新用户 → 提示成功。
3. 重复用同一用户名注册 → 返回 4001。
4. 密码填 3 位 → 返回 4000。
5. `/login/` 用刚注册账号登录 → 成功，返回 is_admin=0。
6. 用 `admin / admin123` 登录 → 成功，返回 is_admin=1。
7. 登录后 `GET /api/me/` → 返回当前用户信息。
8. `POST /api/logout/` 后再 `GET /api/me/` → 返回 4010。
9. 数据库中 10 家默认餐馆已存在。

**合入顺序：** A 是第一个合入的人。把骨架、`common.py`（返回包装 + 装饰器）、models 与迁移、初始化数据、4 个接口、两个页面一起推送到代码库主分支，通知 B/C/D 拉取后即可并行开发。

---

## 3. 交付物清单

- [ ] Django 项目骨架（可 `runserver`）
- [ ] `app/models.py` 三张表 + 迁移文件
- [ ] 初始化数据迁移（默认管理员 + 10 餐馆，管理员密码经 `make_password`）
- [ ] `app/common.py`：统一返回包装 + 错误码常量 + 两个装饰器
- [ ] 接口 #1 #2 #3 #11 及路由
- [ ] `templates/register.html`、`templates/login.html`
- [ ] 自测清单 9 项全部通过
- [ ] 已合入主分支并通知队友

---

## 4. 易错点提醒

1. **默认管理员密码必须 `make_password`**，写明文哈希占位串会导致登不进去——最常见的坑。
2. **建表只走 `migrate`**，不要再手工跑原生建表 SQL，否则与迁移冲突。
3. **返回包装与装饰器是全队公共件**，接口签名定好后尽量稳定，不要频繁改。
4. **校验顺序先格式（4000）后业务（4001/4002）**，不要颠倒。
5. **fetch 必须带 `credentials: 'same-origin'`**，否则 Session Cookie 不发送，登录态失效。
6. models 改字段后记得重新 `makemigrations && migrate`。
