import json
import random

from django.views.decorators.csrf import csrf_exempt

from .common import CODE_NO_CANDIDATE, CODE_PARAM, api_response, login_required_api
from .models import DrawHistory, Restaurant, User


def _body(request):
    try:
        return json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None


@csrf_exempt
@login_required_api
def random_dinner(request):
    if request.method != "POST":
        return api_response(CODE_PARAM, msg="请使用 POST")

    data = _body(request)
    if data is None:
        return api_response(CODE_PARAM, msg="请求体格式错误")

    category = (data.get("category") or "").strip().lower()
    queryset = Restaurant.objects.filter(is_active=True, is_deleted=False)
    if category:
        queryset = queryset.filter(category=category)

    restaurants = list(queryset)
    if not restaurants:
        return api_response(CODE_NO_CANDIDATE)

    total_weight = sum(item.weight for item in restaurants)
    point = random.randint(1, total_weight)
    current = 0
    picked = restaurants[0]
    for item in restaurants:
        current += item.weight
        if point <= current:
            picked = item
            break

    picked.draw_count += 1
    picked.save(update_fields=["draw_count"])

    user = User.objects.get(id=request.session["user_id"])
    history = DrawHistory.objects.create(
        user=user,
        restaurant=picked,
        restaurant_name=picked.name,
    )

    return api_response(
        data={
            "restaurant_id": picked.id,
            "name": picked.name,
            "category": picked.category,
            "avg_price": picked.avg_price,
            "weight": picked.weight,
            "history_id": history.id,
            "drawn_at": history.drawn_at.strftime("%Y-%m-%d %H:%M:%S"),
        },
        msg="今晚就吃它！",
    )


@login_required_api
def draw_history(request):
    if request.method != "GET":
        return api_response(CODE_PARAM, msg="请使用 GET")

    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
    except (TypeError, ValueError):
        return api_response(CODE_PARAM, msg="分页参数需为整数")

    if page < 1 or page_size < 1:
        return api_response(CODE_PARAM, msg="分页参数需为正整数")
    if page_size > 100:
        page_size = 100

    queryset = DrawHistory.objects.filter(user_id=request.session["user_id"])
    total = queryset.count()
    offset = (page - 1) * page_size
    history_list = queryset[offset : offset + page_size]

    return api_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "list": [
                {
                    "id": item.id,
                    "restaurant_id": item.restaurant_id,
                    "restaurant_name": item.restaurant_name,
                    "drawn_at": item.drawn_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for item in history_list
            ],
        }
    )
