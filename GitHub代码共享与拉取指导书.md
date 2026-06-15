# 代码共享与拉取操作指导书（GitHub）

> 适用项目：随机晚饭决定器后台系统
> 适用对象：A 同学（负责共享底座代码）+ B/C/D 同学（负责拉取并接入）
> 平台：GitHub

本指导书分两部分：
- **第一部分**：A 同学如何把已完成的底座代码共享到 GitHub。
- **第二部分**：B/C/D 同学如何拉取代码并在本地跑起来。

请按顺序逐步执行，每一步确认成功再进入下一步。

---

## 第一部分：A 同学共享代码到 GitHub

### 步骤 1：创建 .gitignore（关键，先做）

在**项目根目录**（含 `manage.py` 的目录）新建文件 `.gitignore`，内容如下：

```
__pycache__/
*.pyc
db.sqlite3
.venv/
venv/
.env
.idea/
.vscode/
*.log
```

> **为什么重要：**
> - `db.sqlite3` 必须忽略——每个人本地各跑各的数据库（这正是「各自电脑独立开发」的设计），数据库文件不进仓库，否则队友拉取后会与本地冲突。
> - `__pycache__/`、`.venv/` 是本地缓存和虚拟环境，不应共享。
> - **注意：迁移文件 `app/migrations/*.py` 必须提交，不要忽略、不要删除**，B/C/D 靠它 `migrate` 重建出完全一致的表结构和初始数据。

### 步骤 2：写一个简短的 README.md

在项目根目录新建 `README.md`，方便队友自助启动（省去反复来问）：

```markdown
# 随机晚饭决定器后台系统

## 环境要求
- Python 3.x
- Django

## 本地启动
\`\`\`bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install django
python manage.py migrate          # 建表 + 写入初始化数据
python manage.py runserver
\`\`\`

## 默认管理员账号
- 用户名：admin
- 密码：admin123

## 接口前缀
所有接口以 /api/ 为前缀，统一返回 {code, msg, data} 结构。
```

### 步骤 3：本地初始化 Git 并提交

在项目根目录依次执行：

```bash
git init
git add .
git commit -m "A模块：项目骨架+统一返回+鉴权装饰器+注册登录登出+初始化数据"
```

> 如果是第一次用 Git，需先配置身份（只需配一次）：
> ```bash
> git config --global user.name "你的名字"
> git config --global user.email "你的邮箱"
> ```

### 步骤 4：在 GitHub 创建远程仓库

1. 登录 GitHub，点右上角 **+** → **New repository**。
2. 填写仓库名，例如 `dinner-decider`。
3. 可设为 **Private**（私有，仅团队可见）或 Public。
4. **重要：不要勾选** "Add a README file"、"Add .gitignore"、"Choose a license"。
   （勾了会让远程先有提交，导致下面 push 被拒，需要额外合并。）
5. 点 **Create repository**。
6. 创建后页面会显示仓库地址，形如：
   `https://github.com/你的用户名/dinner-decider.git`

### 步骤 5：关联远程仓库并推送

把下面的地址换成你自己仓库的地址：

```bash
git branch -M main
git remote add origin https://github.com/你的用户名/dinner-decider.git
git push -u origin main
```

> 如果推送时要求登录：GitHub 现在不支持账号密码，需用 **Personal Access Token**。
> 生成方式：GitHub → Settings → Developer settings → Personal access tokens → Generate new token，勾选 `repo` 权限，生成后把这串 token 当作密码粘贴即可。

### 步骤 6：邀请队友（私有仓库才需要）

如果仓库是 Private，需把 B/C/D 加为协作者：

1. 进入仓库 → **Settings** → **Collaborators**。
2. 点 **Add people**，输入队友的 GitHub 用户名邀请。
3. 队友在自己邮箱/GitHub 通知里点 **Accept** 接受邀请。

（Public 仓库可跳过本步，任何人都能 clone。）

### 步骤 7：通知队友并验证

1. 把仓库地址 `https://github.com/你的用户名/dinner-decider.git` 发到团队群。
2. 建议先让**一位队友按第二部分 clone 一遍**，确认能 `migrate` + `runserver` 成功，验证骨架干净可用，再让其他人接入。

✅ 到这里 A 的共享工作完成。

---

## 第二部分：B/C/D 同学拉取代码并本地运行

### 步骤 1：克隆仓库

打开终端，进入你想存放项目的目录，执行（地址用 A 发的）：

```bash
git clone https://github.com/A的用户名/dinner-decider.git
cd dinner-decider
```

> 私有仓库需先接受 A 的协作者邀请，clone 时可能要求输入 GitHub 用户名和 Personal Access Token（同上）。

### 步骤 2：创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install django
```

### 步骤 3：建表 + 初始化数据

```bash
python manage.py migrate
```

> 这一步会在你**本地**根据迁移文件自动重建三张表，并写入默认管理员和 10 家餐馆。
> 你的 `db.sqlite3` 是本地独有的，不会和别人冲突。

### 步骤 4：启动并验证

```bash
python manage.py runserver
```

浏览器访问 `http://127.0.0.1:8000/`，并用默认管理员 `admin / admin123` 测试登录接口，确认底座可用。

### 步骤 5：开始开发自己的模块

- 在 `app/urls.py` 中追加你负责的接口路由（不要删别人的）。
- 在 `app/views.py` 中实现你的接口，**复用 A 提供的公共件**：
  - 统一返回：`from app.common import api_response`
  - 需登录：`@login_required_api`
  - 需管理员：`@admin_required_api`
  - 错误码常量：`from app.common import CODE_PARAM, CODE_FORBIDDEN, ...`

---

## 第三部分：日常协作命令（全员通用）

### 每次开始工作前：先拉取最新代码

```bash
git pull origin main
```

> 养成习惯：**动手前先 pull**，避免基于过时代码开发产生冲突。

### 提交并推送自己的改动

```bash
git add .
git commit -m "B模块：餐馆列表与新增接口"   # 写清楚改了什么
git pull origin main                       # 推送前再拉一次，合并他人改动
git push origin main
```

### 推荐：用分支开发（可选但更安全）

为避免直接在 main 上互相覆盖，可各自开分支：

```bash
git checkout -b feature/restaurant    # 新建并切到自己的分支
# ...开发、commit...
git push -u origin feature/restaurant
```

然后在 GitHub 上发起 **Pull Request** 合并到 main，由 A 或组长 review 后合并。

---

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| push 被拒，提示 rejected / non-fast-forward | 远程有你本地没有的提交 | 先 `git pull origin main` 合并，再 push |
| 创建仓库时 push 失败 | 建仓库时勾了 README/.gitignore | `git pull origin main --allow-unrelated-histories` 后再 push |
| 要求输入密码但报错 | GitHub 不支持密码 | 用 Personal Access Token 当密码 |
| 拉取后 runserver 报「no such table」 | 没执行 migrate | 运行 `python manage.py migrate` |
| 队友的 db.sqlite3 把我的覆盖了 | 数据库文件被误提交 | 确认 `.gitignore` 含 `db.sqlite3`，并 `git rm --cached db.sqlite3` 移出仓库 |
| 改了 models 后表结构没变 | 没生成/执行迁移 | `python manage.py makemigrations && migrate` |

---

## 关键提醒（务必记住）

1. **`db.sqlite3` 不进仓库**，迁移文件 `app/migrations/*.py` **必须进仓库**。
2. **动手前先 `git pull`**，推送前再 `pull` 一次，减少冲突。
3. **A 的 `common.py`（返回包装 + 装饰器）是公共件**，B/C/D 直接复用，不要各写一套。
4. commit message 写清楚改了什么模块、什么功能，方便回溯。
5. 私有仓库记得邀请协作者；GitHub 登录用 Personal Access Token。
