# orders/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory
from products.models import Product
from .middleware import get_current_request, get_client_ip


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    """
    Pre-save signal for Order:
    - Track old status (_old_status)
    - Detect if status changed (_status_changed)
    - Update status_changed_at if status changes
    """
    # New object → no old status
    if not instance.pk:
        instance._old_status = None
        instance._status_changed = True
        return

    # Existing object → fetch old status safely
    try:
        old = Order.objects.only("status").get(pk=instance.pk)
        instance._old_status = old.status
        instance._status_changed = old.status != instance.status

        if instance._status_changed:
            instance.status_changed_at = timezone.now()
    except Order.DoesNotExist:
        # Should rarely happen
        instance._old_status = None
        instance._status_changed = True


@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    """
    Post-save signal:
    - Create OrderStatusHistory entry if status changed
    - Only one entry per logical change
    """
    if not getattr(instance, "_status_changed", False):
        return

    request = get_current_request()
    OrderStatusHistory.objects.create(
        order=instance,
        old_status=instance._old_status,
        new_status=instance.status,
        changed_by=str(getattr(request, "user", None)) if request else None,
        change_source="api" if request else "system",
        ip_address=get_client_ip(request),
    )

    # Prevent duplicate history on repeated saves
    instance._status_changed = False


@receiver(post_save, sender=Order)
def update_stock_on_order(sender, instance, created, **kwargs):
    """
    Post-save signal:
    - Decrease product stock on order creation
    - Restore stock if order is cancelled
    """
    product = instance.product
    old_status = getattr(instance, "_old_status", None)

    # Order created → decrease stock
    if created:
        product.stock_quantity -= instance.quantity
        product.save(update_fields=["stock_quantity"])
        return

    # Order cancelled → restore stock
    if old_status != Order.STATUS_CANCELLED and instance.status == Order.STATUS_CANCELLED:
        product.stock_quantity += instance.quantity
        product.save(update_fields=["stock_quantity"])
