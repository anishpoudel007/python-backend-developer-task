import pytest
from categories.models import Category
from products.models import Product
from orders.models import Order


@pytest.mark.django_db
def test_status_history_created_on_status_change():
    cat = Category.objects.create(name="Electronics")
    prod = Product.objects.create(
        name="iPhone",
        code="IP12",
        description="IP12 desc",
        category=cat,
        base_price=1000,
        stock_quantity=10,
    )
    order = Order.objects.create(
        product=prod, quantity=1, unit_price=prod.final_price)
    order.status = 10
    order.save()
    assert order.status_history.filter(new_status=10).exists()


@pytest.mark.django_db
def test_stock_updates_on_order_create_and_cancel():
    cat = Category.objects.create(name="Electronics")
    prod = Product.objects.create(
        name="iPhone",
        code="IP12",
        description="IP12 desc",
        category=cat,
        base_price=1000,
        stock_quantity=10,
    )
    order = Order.objects.create(
        product=prod, quantity=2, unit_price=prod.final_price)
    prod.refresh_from_db()
    assert prod.stock_quantity == 8
    order.status = 50  # cancelled
    order.save()
    prod.refresh_from_db()
    assert prod.stock_quantity == 10


@pytest.mark.django_db
def test_status_changed_at_updates_on_status_change():
    cat = Category.objects.create(name="Electronics")
    prod = Product.objects.create(
        name="iPhone",
        code="IP12",
        description="IP12 desc",
        category=cat,
        base_price=1000,
        stock_quantity=10,
    )
    order = Order.objects.create(
        product=prod, quantity=1, unit_price=prod.final_price)

    assert order.status_changed_at is None

    # First change
    order.status = 10
    order.save()
    order.refresh_from_db()
    first_ts = order.status_changed_at

    # Second change
    order.status = 20
    order.save()
    order.refresh_from_db()

    assert order.status_changed_at > first_ts
