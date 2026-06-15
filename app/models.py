from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=30)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_user"


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, default="other")
    avg_price = models.IntegerField(default=0)
    weight = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    draw_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_restaurant"


class DrawHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    restaurant = models.ForeignKey(
        Restaurant,
        null=True,
        on_delete=models.SET_NULL,
        db_column="restaurant_id",
    )
    restaurant_name = models.CharField(max_length=100)
    drawn_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_draw_history"
