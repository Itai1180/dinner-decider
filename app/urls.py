from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.index_placeholder),
    path("api/register/", views.register),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/me/", views.me),
    path("register/", TemplateView.as_view(template_name="register.html")),
    path("login/", TemplateView.as_view(template_name="login.html")),
]
