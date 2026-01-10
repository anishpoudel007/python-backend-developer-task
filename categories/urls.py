from django.urls import path
from .views import (
    CategoryListCreateAPIView,
    CategoryRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path("categories/", CategoryListCreateAPIView.as_view()),
    path("categories/<uuid:id>/", CategoryRetrieveUpdateDeleteAPIView.as_view()),
]
