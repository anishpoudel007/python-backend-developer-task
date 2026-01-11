from django.urls import path
from .views import (
    CategoryListCreateAPIView,
    CategoryRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path("/", CategoryListCreateAPIView.as_view()),
    path("/<uuid:id>/", CategoryRetrieveUpdateDeleteAPIView.as_view()),
]
