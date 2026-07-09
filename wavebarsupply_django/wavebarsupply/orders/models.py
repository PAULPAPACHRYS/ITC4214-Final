from django.conf import settings
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # True only while this order is the user's in-progress cart. A placed order
    # has is_cart=False, so a placed 'pending' order is never mistaken for a cart.
    is_cart = models.BooleanField(default=False)

    # Delivery details, filled in when the order is finalised at checkout.
    delivery_name = models.CharField(max_length=100, blank=True, default='')
    delivery_address = models.CharField(max_length=200, blank=True, default='')
    delivery_phone = models.CharField(max_length=20, blank=True, default='')
    delivery_email = models.EmailField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order #{self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalogue.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.quantity} x {self.product} (order #{self.order_id})"
