from django.urls import path
from .views import (
    ProductListCreateAPIView,
    ProductRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path("/", ProductListCreateAPIView.as_view()),
    path("/<uuid:id>/", ProductRetrieveUpdateDeleteAPIView.as_view()),
]
