from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="Home"),
    path("home/login", views.loginForm, name="Login"),
    path("home/register", views.registerForm, name="Register"),
    path("home/logout", views.logout_request, name="Logout"),
    path("admin/", views.admin_panel, name="Admin"),
]