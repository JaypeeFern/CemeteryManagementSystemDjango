from django.urls import path
from . import views


urlpatterns = [
    path("", views.RenderDeceasedSearch, name="Search"),
    path('tables/',views.tables, name='tables')
]