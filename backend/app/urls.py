from django.urls import path

from . import random_views, restaurant_views, views

urlpatterns = [
    path("api/register/", views.register),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/me/", views.me),
    path("api/restaurants/", restaurant_views.restaurant_list_or_create),
    path("api/restaurants/<int:restaurant_id>/", restaurant_views.restaurant_detail),
    path("api/restaurants/<int:restaurant_id>/toggle/", restaurant_views.restaurant_toggle),
    path("api/random-dinner/", random_views.random_dinner),
    path("api/history/", random_views.draw_history),
]
