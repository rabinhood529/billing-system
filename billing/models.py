
import uuid

from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.utils import timezone

from customers.models import Customer
from products.models import Product


class Invoice(models.Model):

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('qr', 'QR Payment'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
    ]

    PAYMENT_STATUSES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
    ]

    INVOICE_STATUSES = [
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )

    customer_name = models.CharField(
        max_length=200,
        default='Walk-in Customer'
    )

    created_by = models.ForeignKey(
    'auth.User',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='created_invoices'
)

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUSES,
        default='unpaid'
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUSES,
        default='completed'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            date_part = timezone.localdate().strftime('%Y%m%d')
            unique_part = uuid.uuid4().hex[:8].upper()
            self.invoice_number = f'INV-{date_part}-{unique_part}'

        super().save(*args, **kwargs)

    @property
    def due_amount(self):
        return self.total - self.amount_paid

    def __str__(self):
        return self.invoice_number

    class Meta:
        ordering = ['-created_at']


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='invoice_items'
    )

    product_name = models.CharField(max_length=200)

    product_code = models.CharField(max_length=50)

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name='invoice_item_quantity_at_least_one'
            )
        ]
