from django.urls import path
from . import views

urlpatterns = [
    path("", views.renderGraveLocator, name="Locator"),
    path('search/', views.searchResults, name='SearchResults'),
    path('search/results/<str:pk>', views.specificSearch, name='SpecificSearch'),
]