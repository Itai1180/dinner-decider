import json

from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .common import (
    CODE_LOGIN_FAIL,
    CODE_PARAM,
    CODE_USERNAME,
    api_response,
    login_required_api,
)
from .models import User


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None


@csrf_exempt
def register(request):
    if request.method != "POST":
        return api_response(CODE_PARAM, msg="请使用 POST")

    data = _body(request)
    if data is None:
        return api_response(CODE_PARAM, msg="请求体格式错误")

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or "").strip()

    if not (1 <= len(username) <= 50):
        return api_response(CODE_PARAM, msg="用户名长度需为 1~50")
    if not (6 <= len(password) <= 128):
        return api_response(CODE_PARAM, msg="密码长度需为 6~128")
    if not (1 <= len(nickname) <= 30):
        return api_response(CODE_PARAM, msg="昵称长度需为 1~30")

    if User.objects.filter(username=username).exists():
        return api_response(CODE_USERNAME)

    user = User.objects.create(
        username=username,
        password=make_password(password),
        nickname=nickname,
        is_admin=False,
    )
    return api_response(data={"user_id": user.id, "username": user.username})


@csrf_exempt
def login(request):
    if request.method != "POST":
        return api_response(CODE_PARAM, msg="请使用 POST")

    data = _body(request)
    if data is None:
        return api_response(CODE_PARAM, msg="请求体格式错误")

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return api_response(CODE_PARAM, msg="账号或密码不能为空")

    user = User.objects.filter(username=username).first()
    if user is None or not check_password(password, user.password):
        return api_response(CODE_LOGIN_FAIL)

    request.session["user_id"] = user.id
    return api_response(
        data={
            "user_id": user.id,
            "nickname": user.nickname,
            "is_admin": 1 if user.is_admin else 0,
        }
    )


@csrf_exempt
def logout(request):
    request.session.flush()
    return api_response(data=None)


@login_required_api
def me(request):
    if request.method != "GET":
        return api_response(CODE_PARAM, msg="请使用 GET")

    user = User.objects.get(id=request.session["user_id"])
    return api_response(
        data={
            "user_id": user.id,
            "nickname": user.nickname,
            "is_admin": 1 if user.is_admin else 0,
        }
    )


def index_placeholder(request):
    return HttpResponse("Dinner index placeholder")
