from django.urls import path
from .views import (
    OrderListCreateAPIView,
    OrderRetrieveUpdateAPIView,
    OrderStatusHistoryAPIView,
)

urlpatterns = [
    path("/", OrderListCreateAPIView.as_view()),
    path("/<uuid:id>/", OrderRetrieveUpdateAPIView.as_view()),
    path("/<uuid:id>/history/", OrderStatusHistoryAPIView.as_view()),
]
