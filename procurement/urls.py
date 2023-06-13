from django.urls import path
from . import views


urlpatterns = [
    path("", views.RenderLotProcurement, name="Procurement"),
    path('customer/', views.customerForm, name='customerForm'),
]