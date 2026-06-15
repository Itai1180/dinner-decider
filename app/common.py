from functools import wraps

from django.http import JsonResponse

from .models import User

# 错误码常量（全队共用）
CODE_OK = 200
CODE_PARAM = 4000
CODE_USERNAME = 4001
CODE_LOGIN_FAIL = 4002
CODE_FORBIDDEN = 4003
CODE_NO_CANDIDATE = 4004
CODE_WEIGHT = 4005
CODE_NOT_FOUND = 4006
CODE_UNAUTH = 4010
CODE_SERVER = 5000

DEFAULT_MSG = {
    CODE_OK: "操作成功",
    CODE_PARAM: "参数错误",
    CODE_USERNAME: "用户名为空或已存在",
    CODE_LOGIN_FAIL: "账号或密码错误",
    CODE_FORBIDDEN: "无权限",
    CODE_NO_CANDIDATE: "无可用候选餐馆",
    CODE_WEIGHT: "权重非法（需1~100的整数）",
    CODE_NOT_FOUND: "资源不存在",
    CODE_UNAUTH: "未登录",
    CODE_SERVER: "服务器内部错误",
}


def api_response(code=CODE_OK, data=None, msg=None):
    """统一返回包装：{code, msg, data}，HTTP 状态码恒为 200。"""
    if msg is None:
        msg = DEFAULT_MSG.get(code, "")
    return JsonResponse({"code": code, "msg": msg, "data": data})


def login_required_api(view_func):
    """需登录：无有效 Session 返回 4010。"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get("user_id")
        if not uid or not User.objects.filter(id=uid).exists():
            return api_response(CODE_UNAUTH)
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required_api(view_func):
    """需管理员：未登录 4010，非管理员 4003。"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get("user_id")
        user = User.objects.filter(id=uid).first() if uid else None
        if user is None:
            return api_response(CODE_UNAUTH)
        if not user.is_admin:
            return api_response(CODE_FORBIDDEN)
        return view_func(request, *args, **kwargs)

    return wrapper
