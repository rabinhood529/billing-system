
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from decimal import Decimal, InvalidOperation


def validate_product_data(request, product=None):

    errors = {}

    name = request.POST.get('name', '').strip()
    product_code = request.POST.get('product_code', '').strip()
    category = request.POST.get('category', '').strip()
    purchase_price = request.POST.get('purchase_price', '').strip()
    selling_price = request.POST.get('selling_price', '').strip()
    stock_quantity = request.POST.get('stock_quantity', '').strip()
    description = request.POST.get('description', '').strip()

    form_data = {
        'name': name,
        'product_code': product_code,
        'category': category,
        'purchase_price': purchase_price,
        'selling_price': selling_price,
        'stock_quantity': stock_quantity,
        'description': description,
    }

    # 1. Product name
    if len(name) < 2:
        errors['name'] = 'Product name must contain at least 2 characters.'
    elif name.isdigit():
        errors['name'] = 'Product name cannot contain only numbers.'
    elif len(name) > 200:
        errors['name'] = 'Product name cannot exceed 200 characters.'

    # 2. Product code
    if len(product_code) < 3:
        errors['product_code'] = 'Product code must contain at least 3 characters.'
    elif len(product_code) > 50:
        errors['product_code'] = 'Product code cannot exceed 50 characters.'
    else:
        duplicate_codes = Product.objects.filter(
            product_code__iexact=product_code
        )

        if product:
            duplicate_codes = duplicate_codes.exclude(id=product.id)

        if duplicate_codes.exists():
            errors['product_code'] = 'This product code already exists.'

    # 3. Category
    if len(category) < 2:
        errors['category'] = 'Category must contain at least 2 characters.'
    elif len(category) > 100:
        errors['category'] = 'Category cannot exceed 100 characters.'

    # 4. Purchase price
    purchase_price_value = None

    try:
        purchase_price_value = Decimal(purchase_price)

        if not purchase_price_value.is_finite() or purchase_price_value <= 0:
            errors['purchase_price'] = 'Purchase price must be greater than zero.'
        elif purchase_price_value > Decimal('99999999.99'):
            errors['purchase_price'] = 'Purchase price is too large.'
        elif purchase_price_value.as_tuple().exponent < -2:
            errors['purchase_price'] = 'Maximum 2 decimal places allowed.'

    except (InvalidOperation, ValueError):
        errors['purchase_price'] = 'Enter a valid purchase price.'

    # 5. Selling price
    selling_price_value = None

    try:
        selling_price_value = Decimal(selling_price)

        if not selling_price_value.is_finite() or selling_price_value <= 0:
            errors['selling_price'] = 'Selling price must be greater than zero.'
        elif selling_price_value > Decimal('99999999.99'):
            errors['selling_price'] = 'Selling price is too large.'
        elif selling_price_value.as_tuple().exponent < -2:
            errors['selling_price'] = 'Maximum 2 decimal places allowed.'

    except (InvalidOperation, ValueError):
        errors['selling_price'] = 'Enter a valid selling price.'

    # 6. Stock quantity
    stock_value = None

    try:
        stock_value = int(stock_quantity)

        if stock_value < 0:
            errors['stock_quantity'] = 'Stock cannot be negative.'

    except ValueError:
        errors['stock_quantity'] = 'Enter a valid whole number for stock.'

    # 7. Description
    if len(description) > 1000:
        errors['description'] = 'Description cannot exceed 1000 characters.'

    values = {
        'name': name,
        'product_code': product_code,
        'category': category,
        'purchase_price': purchase_price_value,
        'selling_price': selling_price_value,
        'stock_quantity': stock_value,
        'description': description,
    }

    return form_data, errors, values


def product_list(request):

    search_query = request.GET.get('search', '')

    products = Product.objects.all()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            product_code__icontains=search_query
        ) | products.filter(
            category__icontains=search_query
        )

    for product in products:

        if product.stock_quantity == 0:
            product.stock_status = 'Out of Stock'

        elif product.stock_quantity <= 5:
            product.stock_status = 'Low Stock'

        else:
            product.stock_status = 'In Stock'

    context = {
        'products': products,
        'search_query': search_query
    }

    return render(request, 'products/product_list.html', context)


def product_create(request):

    form_data = {}
    errors = {}

    if request.method == 'POST':

        form_data, errors, values = validate_product_data(request)

        if not errors:

            Product.objects.create(**values)

            return redirect('product_list')

    return render(
        request,
        'products/product_form.html',
        {
            'form_data': form_data,
            'errors': errors
        }
    )


def product_edit(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':

        form_data, errors, values = validate_product_data(
            request,
            product
        )

        if not errors:

            for field, value in values.items():
                setattr(product, field, value)

            product.save()

            return redirect('product_list')

    else:

        form_data = {
            'name': product.name,
            'product_code': product.product_code,
            'category': product.category,
            'purchase_price': product.purchase_price,
            'selling_price': product.selling_price,
            'stock_quantity': product.stock_quantity,
            'description': product.description,
        }

        errors = {}

    return render(
        request,
        'products/product_form.html',
        {
            'product': product,
            'form_data': form_data,
            'errors': errors
        }
    )


def product_delete(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':

        product.delete()

        return redirect('product_list')

    return render(
        request,
        'products/product_confirm_delete.html',
        {
            'product': product
        }
    )

def inventory_list(request):

    products = Product.objects.all()

    # Search products by name or product code.
    search_query = request.GET.get('search', '').strip()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            product_code__icontains=search_query
        )

    # Filter products by stock status.
    stock_status = request.GET.get('stock_status', '')

    if stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=5)

    elif stock_status == 'low_stock':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=5)

    elif stock_status == 'out_of_stock':
        products = products.filter(stock_quantity=0)

    # Calculate stock summary.
    total_products = Product.objects.count()

    in_stock_count = Product.objects.filter(
        stock_quantity__gt=5
    ).count()

    low_stock_count = Product.objects.filter(
        stock_quantity__gt=0,
        stock_quantity__lte=5
    ).count()

    out_of_stock_count = Product.objects.filter(
        stock_quantity=0
    ).count()

    # Assign stock labels.
    for product in products:

        if product.stock_quantity == 0:
            product.stock_status = 'Out of Stock'

        elif product.stock_quantity <= 5:
            product.stock_status = 'Low Stock'

        else:
            product.stock_status = 'In Stock'

    context = {
        'products': products,
        'search_query': search_query,
        'selected_stock_status': stock_status,
        'total_products': total_products,
        'in_stock_count': in_stock_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }

    return render(request, 'products/inventory_list.html', context)
