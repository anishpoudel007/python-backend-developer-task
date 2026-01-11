import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from products.models import Product


class Order(models.Model):
    STATUS_PENDING = 0
    STATUS_CONFIRMED = 10
    STATUS_PROCESSING = 20
    STATUS_SHIPPED = 30
    STATUS_DELIVERED = 40
    STATUS_CANCELLED = 50

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_code = models.CharField(max_length=20, unique=True, editable=False)

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orders", db_index=True
    )

    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)

    status_changed_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_code

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = f"ORD-{uuid.uuid4().hex[:10].upper()}"

        if not self.unit_price:
            self.unit_price = self.product.final_price

        self.total_price = Decimal(self.unit_price) * self.quantity

        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="timeline", db_index=True
    )

    old_status = models.IntegerField(null=True)
    new_status = models.IntegerField(db_index=True)
    changed_by = models.CharField(max_length=100, null=True)
    change_source = models.CharField(max_length=20)  # api, admin, system
    ip_address = models.GenericIPAddressField(null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_status_history"


ordering = ["-created_at"]
