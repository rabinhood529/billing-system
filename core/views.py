
from datetime import timedelta

from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from billing.models import Invoice, InvoiceItem
from products.models import Product
from customers.models import Customer
from django.contrib.auth.decorators import login_required

@login_required
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

    # Get the top five selling products
    top_products = (
        InvoiceItem.objects
        .filter(invoice__status='completed')
        .values('product_name')
        .annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_total')
        )
        .order_by('-total_quantity')[:5]
    )

    # Prepare daily sales data for the last 7 days
    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    daily_sales = (
        completed_invoices
        .filter(created_at__date__range=(start_date, today))
        .annotate(sale_date=TruncDate('created_at'))
        .values('sale_date')
        .annotate(total=Sum('total'))
    )

    # Convert sales records into a date-to-total dictionary
    sales_by_date = {
        item['sale_date']: float(item['total'])
        for item in daily_sales
    }

    # Include all 7 days, even when there were no sales
    sales_chart_labels = []
    sales_chart_values = []

    for day_number in range(7):
        current_date = start_date + timedelta(days=day_number)

        sales_chart_labels.append(
            current_date.strftime('%d %b')
        )

        sales_chart_values.append(
            sales_by_date.get(current_date, 0)
        )

    context = {
        'total_sales': total_sales,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_invoices': total_invoices,
        'recent_sales': recent_sales,
        'sales_chart_labels': sales_chart_labels,
        'sales_chart_values': sales_chart_values,
        'top_products': top_products,
    }

    return render(
        request,
        'core/dashboard.html',
        context
    )
