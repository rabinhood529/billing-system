
from django.db import models


class Product(models.Model):

    name = models.CharField(max_length=200)

    product_code = models.CharField(
        max_length=50,
        unique=True
    )

    category = models.CharField(max_length=100)

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock_quantity = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ('increase', 'Stock Increased'),
        ('decrease', 'Stock Decreased'),
        ('sale', 'Stock Sold'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='stock_movements'
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES
    )

    quantity = models.PositiveIntegerField()

    previous_stock = models.PositiveIntegerField()

    new_stock = models.PositiveIntegerField()

    reason = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()}"
