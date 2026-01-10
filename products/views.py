from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(delete_status=0)

        category_id = self.request.query_params.get("category")
        active = self.request.query_params.get("active")
        in_stock = self.request.query_params.get("in_stock")

        if category_id:
            qs = qs.filter(category_id=category_id)

        if active is not None:
            qs = qs.filter(active=active)

        if in_stock == "true":
            qs = qs.filter(stock_quantity__gt=0)
        elif in_stock == "false":
            qs = qs.filter(stock_quantity=0)

        return qs.select_related("category")


class ProductRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Product.objects.filter(delete_status=0).select_related("category")

    def delete(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs["id"], delete_status=0)
        product.delete_status = 1
        product.save(update_fields=["delete_status"])
        return Response(status=status.HTTP_204_NO_CONTENT)
