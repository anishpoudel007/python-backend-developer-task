from project.custom_pagination import StandardResultsSetPagination
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(delete_status=0)  # class attribute
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """
        Allow anyone to list, only authenticated to create.
        """
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class ProductRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    lookup_field = "id"

    def get_permissions(self):
        """
        Allow anyone to list, only authenticated to create.
        """
        if self.request.method == "PATCH":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Product.objects.filter(delete_status=0).select_related("category")

    def delete(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs["id"], delete_status=0)
        product.delete_status = 1
        product.save(update_fields=["delete_status"])
        return Response(status=status.HTTP_204_NO_CONTENT)
