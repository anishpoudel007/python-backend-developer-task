import uuid
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from products.models import Category, Product
from orders.models import Order

fake = Faker()


class Command(BaseCommand):
    help = "Seed realistic test data: categories, products, orders"

    def handle(self, *args, **options):
        self.stdout.write("Seeding test data...")

        # --- Categories ---
        parent_categories = []
        parent_names = ["Electronics", "Home Appliances", "Fashion"]
        for name in parent_names:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"{name} category",
                    "active": 1,
                    "delete_status": 0,
                },
            )
            parent_categories.append(cat)

        sub_categories = []
        for parent in parent_categories:
            for i in range(3):  # 3 subcategories per parent
                sub_name = f"{parent.name} Sub {i + 1}"
                sub, _ = Category.objects.get_or_create(
                    name=sub_name,
                    defaults={
                        "description": f"{sub_name} description",
                        "parent_category": parent,
                        "active": 1,
                        "delete_status": 0,
                    },
                )
                sub_categories.append(sub)

        self.stdout.write(
            f"""Created {len(parent_categories)} parent categories and {
                len(sub_categories)
            } subcategories"""
        )

        # --- Products ---
        products = []
        all_categories = parent_categories + sub_categories
        for i in range(50):  # 50 products
            category = random.choice(all_categories)
            code = f"P{i + 1:03d}-{uuid.uuid4().hex[:6].upper()}"
            prod, _ = Product.objects.get_or_create(
                code=code,
                defaults={
                    "name": fake.unique.word().title(),
                    "category": category,
                    "description": fake.sentence(),
                    "base_price": Decimal(random.randint(50, 5000)),
                    "discount_percent": random.randint(0, 50),
                    "stock_quantity": random.randint(0, 100),
                    "active": 1,
                    "delete_status": 0,
                },
            )
            products.append(prod)

        self.stdout.write(f"Created {len(products)} products")

        # --- Orders ---
        orders = []
        for i in range(100):  # 100 orders
            product = random.choice(products)
            quantity = random.randint(1, min(5, product.stock_quantity or 1))
            order, _ = Order.objects.get_or_create(
                product=product,
                quantity=quantity,
                defaults={
                    "unit_price": product.final_price,
                    # pending, confirmed, processing
                    "status": random.choice([0, 10, 20]),
                    "status_changed_at": timezone.now(),
                },
            )
            # Adjust stock for created orders
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                product.save(update_fields=["stock_quantity"])
            orders.append(order)

        self.stdout.write(f"Created {len(orders)} orders")
        self.stdout.write(self.style.SUCCESS(
            "Random test data seeded successfully!"))
