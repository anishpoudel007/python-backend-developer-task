from django.urls import path
from .views import (
    ProductListCreateAPIView,
    ProductRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path("products/", ProductListCreateAPIView.as_view()),
    path("products/<uuid:id>/", ProductRetrieveUpdateDeleteAPIView.as_view()),
]
