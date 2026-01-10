from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from .models import Order, OrderStatusHistory
from .serializers import OrderSerializer, OrderStatusHistorySerializer


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.all().select_related("product")

        status = self.request.query_params.get("status")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if status is not None:
            qs = qs.filter(status=status)

        if start_date:
            qs = qs.filter(created_at__date__gte=parse_date(start_date))

        if end_date:
            qs = qs.filter(created_at__date__lte=parse_date(end_date))

        return qs


class OrderRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.select_related("product").prefetch_related("status_history")


class OrderStatusHistoryAPIView(generics.ListAPIView):
    serializer_class = OrderStatusHistorySerializer

    def get_queryset(self):
        order = get_object_or_404(Order, id=self.kwargs["id"])
        return order.status_history.all()
