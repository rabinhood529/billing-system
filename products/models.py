
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
