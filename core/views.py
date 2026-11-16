
from django.shortcuts import render
from django.db.models import Sum

from billing.models import Invoice
from products.models import Product
from customers.models import Customer


def dashboard(request):

    # Only completed invoices count
    completed_invoices = Invoice.objects.filter(
        status='completed'
    )

    # Calculate total sales
    total_sales = completed_invoices.aggregate(
        total=Sum('total')
    )['total'] or 0

    # Count total records
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_invoices = completed_invoices.count()

    # Get the latest five completed invoices
    recent_sales = completed_invoices.order_by(
        '-created_at'
    )[:5]

    context = {
        'total_sales': total_sales,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_invoices': total_invoices,
        'recent_sales': recent_sales,
    }

    return render(
        request,
        'core/dashboard.html',
        context
    )
