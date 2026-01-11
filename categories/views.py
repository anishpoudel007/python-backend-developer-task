from project.custom_pagination import StandardResultsSetPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Category
from .serializers import CategorySerializer
from rest_framework import generics, permissions, status


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """
        Allow anyone to list, only authenticated to create.
        """
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Category.objects.filter(
            parent_category__isnull=True, delete_status=0
        ).prefetch_related("children")

    def perform_create(self, serializer):
        serializer.save()


class CategoryRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CategorySerializer
    lookup_field = "id"

    def get_permissions(self):
        """
        Allow anyone to list, only authenticated to create.
        """
        if self.request.method == "PATCH":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Category.objects.filter(delete_status=0)

    def delete(self, request, *args, **kwargs):
        category = get_object_or_404(Category, id=kwargs["id"], delete_status=0)
        category.delete_status = 1
        category.save(update_fields=["delete_status"])
        return Response(status=status.HTTP_204_NO_CONTENT)
