from rest_framework import serializers
from django.utils import timezone
from products.models import Product
from .models import Order, OrderStatusHistory


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "code", "stock_quantity"]


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
        """
        Ensure product exists and is active/not deleted.
        """
        try:
            product = Product.objects.get(id=value, delete_status=0, active=1)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive product")
        return value

    def validate(self, attrs):
        """
        Check stock before saving.
        """
        if self.instance is None:
            product_id = attrs.get("product_id")
            quantity = attrs.get("quantity")

            if not product_id:
                raise serializers.ValidationError({"product_id": "This field is required."})

            if quantity is None or quantity <= 0:
                raise serializers.ValidationError({"quantity": "Must be greater than 0"})

            product = Product.objects.select_for_update().get(id=product_id)

            if product.stock_quantity < quantity:
                raise serializers.ValidationError("Not enough stock")

        return attrs
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 0)

        print("Product ID", product_id)

        product = Product.objects.get(id=product_id)

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")

        if product.stock_quantity < quantity:
            raise serializers.ValidationError("Not enough stock for this product")

        return attrs

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
        validated_data.pop("product_id", None)
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
