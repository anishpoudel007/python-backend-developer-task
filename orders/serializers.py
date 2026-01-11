from rest_framework import serializers
from django.utils import timezone
from products.models import Product
from .models import Order, OrderStatusHistory


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "code"]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = [
            "id",
            "old_status",
            "new_status",
            "changed_by",
            "change_source",
            "ip_address",
            "notes",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    timeline = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_code",
            "product",
            "product_id",
            "quantity",
            "unit_price",
            "total_price",
            "status",
            "status_changed_at",
            "created_at",
            "updated_at",
            "timeline",
        ]
        read_only_fields = [
            "order_code",
            "unit_price",
            "total_price",
            "status_changed_at",
        ]

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, delete_status=0, active=1).exists():
            raise serializers.ValidationError("Invalid or inactive product")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        product = Product.objects.get(id=product_id)

        order = Order.objects.create(
            product=product,
            quantity=validated_data["quantity"],
            unit_price=product.final_price,
            status=Order.STATUS_PENDING,
        )

        OrderStatusHistory.objects.create(
            order=order, old_status=None, new_status=order.status, change_source="api"
        )

        return order

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")

        if new_status is not None and new_status != instance.status:
            OrderStatusHistory.objects.create(
                order=instance,
                old_status=instance.status,
                new_status=new_status,
                changed_by=self.context.get("user"),
                change_source="api",
                ip_address=self.context.get("ip"),
            )
            instance.status_changed_at = timezone.now()

        return super().update(instance, validated_data)
