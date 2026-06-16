"""
B同学负责：餐馆管理接口
- #4  GET   /api/restaurants/       餐馆列表（分页/筛选）
- #5  POST  /api/restaurants/       新增餐馆
- #6  PUT   /api/restaurants/{id}/  编辑餐馆
- #7  DELETE /api/restaurants/{id}/ 删除餐馆（软删除）
- #8  PATCH /api/restaurants/{id}/toggle/  启用/禁用
"""

import json

from django.views.decorators.csrf import csrf_exempt

from .common import (
    CODE_OK,
    CODE_PARAM,
    CODE_FORBIDDEN,
    CODE_WEIGHT,
    CODE_NOT_FOUND,
    CODE_UNAUTH,
    CODE_SERVER,
    api_response,
    login_required_api,
    admin_required_api,
)
from .models import Restaurant

# 合法的分类枚举
VALID_CATEGORIES = {"fastfood", "hotpot", "snack", "chinese", "western", "other"}


def _body(request):
    """解析请求体 JSON"""
    try:
        return json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None


def _validate_restaurant_params(data, is_create=True):
    """
    校验餐馆参数，返回 (is_valid, error_code, error_msg, cleaned_data)
    is_create: True=新增时需要所有必填字段；False=编辑时只需校验传入字段
    """
    errors = []
    cleaned = {}

    # name
    name = (data.get("name") or "").strip()
    if is_create:
        if not name:
            errors.append("餐馆名称不能为空")
        elif len(name) > 100:
            errors.append("餐馆名称长度不能超过100")
    else:
        if name:
            if len(name) > 100:
                errors.append("餐馆名称长度不能超过100")
            cleaned["name"] = name
    if name:
        cleaned["name"] = name

    # category
    category = (data.get("category") or "").strip().lower()
    if is_create:
        if not category:
            errors.append("分类不能为空")
        elif category not in VALID_CATEGORIES:
            errors.append("分类不合法，可选：fastfood/hotpot/snack/chinese/western/other")
    else:
        if category:
            if category not in VALID_CATEGORIES:
                errors.append("分类不合法，可选：fastfood/hotpot/snack/chinese/western/other")
            cleaned["category"] = category
    if category:
        cleaned["category"] = category

    # avg_price
    if "avg_price" in data:
        try:
            price = int(data["avg_price"])
            if price < 0:
                errors.append("人均价格不能为负数")
            cleaned["avg_price"] = price
        except (ValueError, TypeError):
            errors.append("人均价格需为整数")

    # weight
    if is_create or "weight" in data:
        try:
            weight = int(data["weight"])
            if weight < 1 or weight > 100:
                errors.append("权重需为1~100的整数")
            cleaned["weight"] = weight
        except (ValueError, TypeError):
            errors.append("权重需为1~100的整数")

    # is_active
    if "is_active" in data:
        cleaned["is_active"] = 1 if data["is_active"] else 0

    if errors:
        # 根据错误内容选择合适的错误码
        weight_errors = [e for e in errors if '权重' in e]
        if weight_errors and len(weight_errors) == len(errors):
            return False, CODE_WEIGHT, "; ".join(errors), None
        return False, CODE_PARAM, "; ".join(errors), None

    return True, CODE_OK, "", cleaned


# ====================== #4 GET 列表 & #5 POST 新增 ======================

@csrf_exempt
def restaurant_list_or_create(request):
    """
    根据请求方法分发：
    GET  -> 餐馆列表（需登录，所有用户可访问）
    POST -> 新增餐馆（需管理员）
    """
    if request.method == "GET":
        return _restaurant_list(request)
    elif request.method == "POST":
        return _restaurant_create(request)
    else:
        return api_response(CODE_PARAM, msg="请使用 GET 或 POST")


@login_required_api
def _restaurant_list(request):
    """
    GET /api/restaurants/?is_active=1&category=fastfood&page=1&page_size=10
    所有登录用户均可访问（管理员和普通用户）
    默认仅返回 is_deleted=0 的记录
    按 weight 降序、id 升序排列
    """
    # 获取查询参数
    is_active = request.GET.get("is_active")
    category = request.GET.get("category")
    try:
        page = int(request.GET.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = int(request.GET.get("page_size", 10))
    except (ValueError, TypeError):
        page_size = 10

    # 限制范围
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    if page < 1:
        page = 1

    # 构建查询：默认排除已删除
    queryset = Restaurant.objects.filter(is_deleted=False)

    if is_active is not None:
        queryset = queryset.filter(is_active=1 if is_active in ("1", "true", "True") else 0)

    if category:
        queryset = queryset.filter(category=category)

    # 排序：weight 降序，id 升序
    queryset = queryset.order_by("-weight", "id")

    # 分页
    total = queryset.count()
    offset = (page - 1) * page_size
    restaurants = queryset[offset:offset + page_size]

    list_data = []
    for r in restaurants:
        list_data.append({
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "avg_price": r.avg_price,
            "weight": r.weight,
            "is_active": 1 if r.is_active else 0,
            "draw_count": r.draw_count,
        })

    return api_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": list_data,
    })


@admin_required_api
def _restaurant_create(request):
    """
    POST /api/restaurants/
    需管理员权限
    """
    data = _body(request)
    if data is None:
        return api_response(CODE_PARAM, msg="请求体格式错误")

    is_valid, err_code, err_msg, cleaned = _validate_restaurant_params(data, is_create=True)
    if not is_valid:
        return api_response(err_code, msg=err_msg)

    restaurant = Restaurant.objects.create(
        name=cleaned["name"],
        category=cleaned.get("category", "other"),
        avg_price=cleaned.get("avg_price", 0),
        weight=cleaned["weight"],
        is_active=bool(cleaned.get("is_active", 1)),
        draw_count=0,
        is_deleted=False,
    )

    return api_response(data={
        "id": restaurant.id,
        "name": restaurant.name,
        "weight": restaurant.weight,
        "is_active": 1 if restaurant.is_active else 0,
    })


# ====================== #6 PUT 编辑 & #7 DELETE 删除 ======================

@csrf_exempt
def restaurant_detail(request, restaurant_id):
    """
    根据请求方法分发：
    PUT    -> 编辑餐馆（需管理员）
    DELETE -> 软删除餐馆（需管理员）
    """
    if request.method == "PUT":
        return _restaurant_edit(request, restaurant_id)
    elif request.method == "DELETE":
        return _restaurant_delete(request, restaurant_id)
    else:
        return api_response(CODE_PARAM, msg="请使用 PUT 或 DELETE")


@admin_required_api
def _restaurant_edit(request, restaurant_id):
    """
    PUT /api/restaurants/{id}/
    整体更新（含 is_active），需管理员权限
    """
    data = _body(request)
    if data is None:
        return api_response(CODE_PARAM, msg="请求体格式错误")

    # 查找记录（排除已删除）
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id, is_deleted=False)
    except Restaurant.DoesNotExist:
        return api_response(CODE_NOT_FOUND)

    # 校验参数（编辑模式，必填项允许不传，保持原值）
    is_valid, err_code, err_msg, cleaned = _validate_restaurant_params(data, is_create=False)
    if not is_valid:
        return api_response(err_code, msg=err_msg)

    # 更新字段
    if "name" in cleaned:
        restaurant.name = cleaned["name"]
    if "category" in cleaned:
        restaurant.category = cleaned["category"]
    if "avg_price" in cleaned:
        restaurant.avg_price = cleaned["avg_price"]
    if "weight" in cleaned:
        restaurant.weight = cleaned["weight"]
    if "is_active" in cleaned:
        restaurant.is_active = bool(cleaned["is_active"])

    restaurant.save()

    return api_response(data={
        "id": restaurant.id,
        "name": restaurant.name,
        "weight": restaurant.weight,
        "is_active": 1 if restaurant.is_active else 0,
    })


@admin_required_api
def _restaurant_delete(request, restaurant_id):
    """
    DELETE /api/restaurants/{id}/
    软删除：is_deleted 置 1，保留 draw_count 与历史关联
    需管理员权限
    """
    try:
        restaurant = Restaurant.objects.get(id=restaurant_id, is_deleted=False)
    except Restaurant.DoesNotExist:
        return api_response(CODE_NOT_FOUND)

    restaurant.is_deleted = True
    restaurant.save()

    return api_response(data={
        "id": restaurant.id,
        "deleted": True,
    })


# ====================== #8 PATCH 启用/禁用 ======================

@csrf_exempt
@admin_required_api
def restaurant_toggle(request, restaurant_id):
    """
    PATCH /api/restaurants/{id}/toggle/
    仅切换 is_active，需管理员权限
    Body: {"is_active": 0} 或 {"is_active": 1}
    """
    if request.method != "PATCH":
        return api_response(CODE_PARAM, msg="请使用 PATCH")

    data = _body(request)
    if data is None:
        return api_response(CODE_PARAM, msg="请求体格式错误")

    if "is_active" not in data:
        return api_response(CODE_PARAM, msg="缺少 is_active 参数")

    is_active_val = 1 if data["is_active"] else 0

    try:
        restaurant = Restaurant.objects.get(id=restaurant_id, is_deleted=False)
    except Restaurant.DoesNotExist:
        return api_response(CODE_NOT_FOUND)

    restaurant.is_active = bool(is_active_val)
    restaurant.save()

    return api_response(data={
        "id": restaurant.id,
        "is_active": 1 if restaurant.is_active else 0,
    })
