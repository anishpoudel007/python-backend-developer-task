import pytest
from django.core.exceptions import ValidationError
from categories.models import Category
from products.models import Product
from orders.models import Order


@pytest.mark.django_db
def test_category_creation_with_parent():
    parent = Category.objects.create(name="Electronics")
    child = Category.objects.create(name="Phones", parent_category=parent)
    assert child.parent_category == parent
    assert parent.children.first() == child


@pytest.mark.django_db
def test_product_valid_discount():
    cat = Category.objects.create(name="Electronics")
    prod = Product.objects.create(
        name="iPhone",
        description="iPhone 12",
        code="IP12",
        category=cat,
        base_price=1000,
        discount_percent=10,
    )
    assert prod.final_price == 900
    assert prod.discount_amount == 100


@pytest.mark.django_db
def test_product_invalid_discount():
    cat = Category.objects.create(name="Electronics")
    with pytest.raises(ValidationError):
        Product.objects.create(
            name="iPhone",
            description="iPhone 12",
            code="IP12",
            category=cat,
            base_price=1000,
            discount_percent=120,  # invalid
        )


@pytest.mark.django_db
def test_order_creation_decreases_stock():
    cat = Category.objects.create(name="Electronics")
    prod = Product.objects.create(
        name="iPhone",
        code="IP12",
        description="IP12 description",
        category=cat,
        base_price=1000,
        stock_quantity=10,
    )
    order = Order.objects.create(
        product=prod, quantity=3, unit_price=prod.final_price)
    prod.refresh_from_db()
    assert prod.stock_quantity == 7
