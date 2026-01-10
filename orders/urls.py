from django.urls import path
from .views import (
    OrderListCreateAPIView,
    OrderRetrieveUpdateAPIView,
    OrderStatusHistoryAPIView,
)

urlpatterns = [
    path("orders/", OrderListCreateAPIView.as_view()),
    path("orders/<uuid:id>/", OrderRetrieveUpdateAPIView.as_view()),
    path("orders/<uuid:id>/history/", OrderStatusHistoryAPIView.as_view()),
]
