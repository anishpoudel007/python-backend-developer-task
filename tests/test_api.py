import pytest
from rest_framework.test import APIClient
from categories.models import Category
from products.models import Product
from rest_framework_simplejwt.tokens import RefreshToken
from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username="testuser", password="password123")
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_with_auth(test_user):
    client = APIClient()
    refresh = RefreshToken.for_user(test_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
def test_list_categories_with_subcategories(api_client):
    parent = Category.objects.create(name="Electronics")
    child = Category.objects.create(name="Phones", parent_category=parent)
    res = api_client.get("/api/categories/")
    data = res.json()["results"]
    assert len(data) == 1
    assert data[0]["sub_categories"][0]["name"] == "Phones"


@pytest.mark.django_db
def test_create_product_with_category(api_client_with_auth):
    cat = Category.objects.create(name="Electronics")
    payload = {
        "name": "iPhone",
        "description": "iPhone 12",
        "code": "IP12",
        "category_id": str(cat.id),
        "base_price": "1000",
        "discount_percent": 10,
        "stock_quantity": 5,
    }
    res = api_client_with_auth.post("/api/products/", payload, format="json")
    assert res.status_code == 201
    assert res.json()["category"]["id"] == str(cat.id)


@pytest.mark.django_db
def test_filter_products_by_price_and_stock(api_client):
    cat = Category.objects.create(name="Electronics")
    Product.objects.create(
        name="A", description="A desc", code="A1", category=cat, base_price=500, stock_quantity=5
    )
    Product.objects.create(
        name="B", description="B desc", code="B1", category=cat, base_price=1500, stock_quantity=0
    )
    res = api_client.get("/api/products/?in_stock=true")
    data = res.json()
    assert all(p["stock_quantity"] > 0 for p in data["results"])


@pytest.mark.django_db
def test_update_order_status_creates_history(api_client_with_auth):
    cat = Category.objects.create(name="Electronics")
    prod = Product.objects.create(
        name="iPhone",
        code="IP12",
        description="IP12 desc",
        category=cat,
        base_price=1000,
        stock_quantity=10,
    )
    order = Order.objects.create(product_id=prod.id, quantity=1, unit_price=prod.final_price)
    res = api_client_with_auth.patch(f"/api/orders/{order.id}/", {"status": 10}, format="json")
    assert res.status_code == 200
    order.refresh_from_db()
    assert order.status == 10
    print("History", order.timeline.values("old_status", "new_status"))
    assert order.timeline.count() == 2  # created + status change


@pytest.mark.django_db
def test_soft_delete_category(api_client):
    cat = Category.objects.create(name="Electronics")
    res = api_client.delete(f"/api/categories/{cat.id}/")
    cat.refresh_from_db()
    assert cat.delete_status == 1
