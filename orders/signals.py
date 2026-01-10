from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory
from products.models import Product
from .middleware import get_current_request


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Store old status in instance attribute before save
    """
    if instance.pk:
        old_instance = Order.objects.filter(pk=instance.pk).first()
        instance._old_status = old_instance.status if old_instance else None
    else:
        instance._old_status = None


@receiver(pre_save, sender=Order)
def update_status_timestamp(sender, instance, **kwargs):
    """
    Auto-set status_changed_at if status changes
    """
    old_status = getattr(instance, "_old_status", None)
    if old_status is not None and old_status != instance.status:
        instance.status_changed_at = timezone.now()


@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    """
    Create status history entry if status changed
    """
    old_status = getattr(instance, "_old_status", None)
    if created or (old_status is not None and old_status != instance.status):
        request = get_current_request()
        changed_by = getattr(request, "user", None)
        ip_address = getattr(request, "META", {}).get("REMOTE_ADDR") if request else None
        change_source = "api" if request else "system"

        OrderStatusHistory.objects.create(
            order=instance,
            old_status=old_status,
            new_status=instance.status,
            changed_by=str(changed_by) if changed_by else None,
            change_source=change_source,
            ip_address=ip_address,
        )


@receiver(post_save, sender=Order)
def update_stock_on_order(sender, instance, created, **kwargs):
    """
    Decrease product stock on order creation
    Restore stock if order is cancelled (status=50)
    """
    product = instance.product
    old_status = getattr(instance, "_old_status", None)

    # Order created → decrease stock
    if created:
        if product.stock_quantity >= instance.quantity:
            product.stock_quantity -= instance.quantity
            product.save(update_fields=["stock_quantity"])
        else:
            # Optional: raise exception or log insufficient stock
            raise ValueError("Not enough stock for product")

    # Order cancelled → restore stock
    if old_status != Order.STATUS_CANCELLED and instance.status == Order.STATUS_CANCELLED:
        product.stock_quantity += instance.quantity
        product.save(update_fields=["stock_quantity"])
