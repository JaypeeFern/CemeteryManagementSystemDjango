from django.urls import path
from . import views


urlpatterns = [
    path("", views.RenderDeceasedSearch, name="Search"),
    path('tables/', views.tables, name='tables'),
    path('grave-images/<path:name>', views.private_grave_image, name='PrivateGraveImage'),
    path('grave-image/<int:pk>', views.private_grave_image_for_record, name='PrivateGraveImageForRecord'),
]
