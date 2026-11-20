from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
    'invoice_number',
    'customer_name',
    'created_by',
    'total',
    'payment_method',
    'payment_status',
    'status',
    'created_at',
)

    search_fields = ('invoice_number', 'customer_name')
    list_filter = ('payment_method', 'payment_status', 'status')
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        'invoice',
        'product_name',
        'product_code',
        'quantity',
        'unit_price',
        'line_total',
    )