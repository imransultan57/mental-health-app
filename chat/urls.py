from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("chat/", views.chat_view, name="chat"),
    path("chat_api/", views.chat_api, name="chat_api"),
]
