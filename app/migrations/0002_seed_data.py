from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed(apps, schema_editor):
    User = apps.get_model("app", "User")
    Restaurant = apps.get_model("app", "Restaurant")

    if not User.objects.filter(username="admin").exists():
        User.objects.create(
            username="admin",
            password=make_password("admin123"),
            nickname="管理员",
            is_admin=True,
        )

    data = [
        ("麦当劳", "fastfood", 35, 5),
        ("肯德基", "fastfood", 35, 4),
        ("海底捞", "hotpot", 120, 2),
        ("沙县小吃", "snack", 20, 6),
        ("兰州拉面", "snack", 25, 5),
        ("黄焖鸡米饭", "chinese", 28, 4),
        ("必胜客", "western", 90, 2),
        ("煲仔饭", "chinese", 30, 3),
        ("麻辣烫", "snack", 32, 5),
        ("日式寿司", "western", 110, 1),
    ]
    existing_names = set(Restaurant.objects.values_list("name", flat=True))
    for name, category, avg_price, weight in data:
        if name in existing_names:
            continue
        Restaurant.objects.create(
            name=name,
            category=category,
            avg_price=avg_price,
            weight=weight,
            is_active=True,
            is_deleted=False,
        )


def unseed(apps, schema_editor):
    User = apps.get_model("app", "User")
    Restaurant = apps.get_model("app", "Restaurant")

    User.objects.filter(username="admin").delete()
    Restaurant.objects.filter(
        name__in=[
            "麦当劳",
            "肯德基",
            "海底捞",
            "沙县小吃",
            "兰州拉面",
            "黄焖鸡米饭",
            "必胜客",
            "煲仔饭",
            "麻辣烫",
            "日式寿司",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("app", "0001_initial")]

    operations = [migrations.RunPython(seed, unseed)]
