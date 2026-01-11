from os import name
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(delete_status=0)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering = ["name"]

    def perform_create(self, serializer):
        # Validate category exists and is active/not deleted
        category = serializer.validated_data.get("category")
        if category.delete_status != 0 or category.active != 1:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"category": "Category is inactive or deleted"})
        serializer.save()


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
