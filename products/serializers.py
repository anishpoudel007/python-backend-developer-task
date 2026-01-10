from rest_framework import serializers
from categories.models import Category
from .models import Product


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent_category",
        ]


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)

    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "code",
            "description",
            "category",
            "category_id",
            "base_price",
            "discount_percent",
            "final_price",
            "discount_amount",
            "stock_quantity",
            "in_stock",
            "active",
            "created_at",
            "updated_at",
        ]

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value, delete_status=0, active=1).exists():
            raise serializers.ValidationError("Invalid or inactive category")
        return value

    def create(self, validated_data):
        category_id = validated_data.pop("category_id")
        validated_data["category"] = Category.objects.get(id=category_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop("category_id", None)
        if category_id:
            instance.category = Category.objects.get(id=category_id)
        return super().update(instance, validated_data)
