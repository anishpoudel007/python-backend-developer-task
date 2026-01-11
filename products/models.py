import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", db_index=True
    )

    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    discount_percent = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    stock_quantity = models.IntegerField(default=0)
    active = models.IntegerField(default=1, db_index=True)
    delete_status = models.IntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "active", "delete_status"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()  # 🔥 enforce validation
        super().save(*args, **kwargs)

    # ---- Computed fields ----

    @property
    def discount_amount(self):
        return (self.base_price * Decimal(self.discount_percent)) / Decimal(100)

    @property
    def final_price(self):
        return self.base_price - self.discount_amount

    @property
    def in_stock(self):
        return self.stock_quantity > 0
