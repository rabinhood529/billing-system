
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from products.models import Product
from customers.models import Customer
from .models import Invoice, InvoiceItem


def pos(request):

    products = Product.objects.filter(
        stock_quantity__gt=0
    ).order_by('name')

    customers = Customer.objects.all().order_by('name')

    cart = request.session.get('cart', {})

    cart_items = []
    subtotal = Decimal('0.00')

    for product_id, quantity in cart.items():

        try:
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)

            if quantity < 1:
                continue

            line_total = product.selling_price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'line_total': line_total,
            })

            subtotal += line_total

        except (Product.DoesNotExist, ValueError, TypeError):
            continue

    discount = Decimal(
        str(request.session.get('discount', '0.00'))
    )

    if discount > subtotal:
        discount = Decimal('0.00')
        request.session['discount'] = '0.00'
        messages.warning(
            request,
            'Discount was reset because it exceeded the updated subtotal.'
        )

    grand_total = subtotal - discount

    context = {
        'products': products,
        'customers': customers,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'grand_total': grand_total,
        'selected_customer_id': request.session.get('customer_id'),
    }

    return render(request, 'billing/pos.html', context)


def add_to_cart(request, product_id):

    if request.method == 'POST':

        product = get_object_or_404(Product, id=product_id)

        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid quantity.')
            return redirect('pos')

        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('pos')

        cart = request.session.get('cart', {})

        current_quantity = int(cart.get(str(product.id), 0))
        new_quantity = current_quantity + quantity

        if product.stock_quantity == 0:
            messages.error(request, 'This product is out of stock.')

        elif new_quantity > product.stock_quantity:
            messages.error(
                request,
                f'Only {product.stock_quantity} units of {product.name} are available.'
            )

        else:
            cart[str(product.id)] = new_quantity
            request.session['cart'] = cart

            messages.success(
                request,
                f'{product.name} added to cart.'
            )

    return redirect('pos')


def remove_from_cart(request, product_id):

    if request.method == 'POST':

        cart = request.session.get('cart', {})

        cart.pop(str(product_id), None)

        request.session['cart'] = cart

        messages.success(request, 'Product removed from cart.')

    return redirect('pos')


def update_cart(request, product_id):

    if request.method == 'POST':

        product = get_object_or_404(Product, id=product_id)

        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid quantity.')
            return redirect('pos')

        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')

        elif quantity > product.stock_quantity:
            messages.error(
                request,
                f'Only {product.stock_quantity} units of {product.name} are available.'
            )

        else:
            cart = request.session.get('cart', {})

            cart[str(product.id)] = quantity

            request.session['cart'] = cart

            messages.success(
                request,
                f'{product.name} quantity updated successfully.'
            )

    return redirect('pos')


def update_discount(request):

    if request.method == 'POST':

        cart = request.session.get('cart', {})
        subtotal = Decimal('0.00')

        for product_id, quantity in cart.items():

            try:
                product = Product.objects.get(id=product_id)
                subtotal += product.selling_price * int(quantity)

            except (Product.DoesNotExist, ValueError, TypeError):
                continue

        try:
            discount = Decimal(request.POST.get('discount', '0'))

            if not discount.is_finite():
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            messages.error(request, 'Please enter a valid discount.')
            return redirect('pos')

        if discount < 0:
            messages.error(request, 'Discount cannot be negative.')

        elif discount > subtotal:
            messages.error(
                request,
                'Discount cannot be greater than the subtotal.'
            )

        elif discount.as_tuple().exponent < -2:
            messages.error(
                request,
                'Discount can have a maximum of two decimal places.'
            )

        else:
            request.session['discount'] = str(discount)

            messages.success(request, 'Discount applied successfully.')

    return redirect('pos')


def update_customer(request):

    if request.method == 'POST':

        customer_id = request.POST.get('customer')

        if not customer_id:
            request.session['customer_id'] = None
            messages.success(request, 'Walk-in Customer selected.')

        else:
            customer = Customer.objects.filter(
                id=customer_id
            ).first()

            if customer:
                request.session['customer_id'] = customer.id
                messages.success(
                    request,
                    f'{customer.name} selected successfully.'
                )

            else:
                messages.error(request, 'Invalid customer selected.')

    return redirect('pos')


def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, 'Your shopping cart is empty.')
        return redirect('pos')

    cart_items = []
    subtotal = Decimal('0.00')

    for product_id, quantity in cart.items():

        try:
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)

            if quantity < 1:
                continue

            line_total = product.selling_price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'line_total': line_total,
            })

            subtotal += line_total

        except (Product.DoesNotExist, ValueError, TypeError):
            continue

    if not cart_items:
        messages.error(request, 'No valid products found in your cart.')
        return redirect('pos')

    discount = Decimal(
        str(request.session.get('discount', '0.00'))
    )

    if not discount.is_finite() or discount < 0 or discount > subtotal:
        discount = Decimal('0.00')

    grand_total = subtotal - discount

    customer_id = request.session.get('customer_id')
    customer = Customer.objects.filter(id=customer_id).first()

    # Process the sale when the payment form is submitted.
    if request.method == 'POST':

        payment_method = request.POST.get('payment_method', '')

        if payment_method not in dict(Invoice.PAYMENT_METHODS):
            messages.error(request, 'Please select a valid payment method.')
            return redirect('checkout')

        try:
            amount_paid = Decimal(request.POST.get('amount_paid', ''))

            if not amount_paid.is_finite():
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            messages.error(request, 'Please enter a valid amount paid.')
            return redirect('checkout')

        if amount_paid < 0:
            messages.error(request, 'Amount paid cannot be negative.')
            return redirect('checkout')

        if amount_paid > grand_total:
            messages.error(
                request,
                'Amount paid cannot be greater than the grand total.'
            )
            return redirect('checkout')

        if amount_paid.as_tuple().exponent < -2:
            messages.error(
                request,
                'Amount paid can have a maximum of two decimal places.'
            )
            return redirect('checkout')

        try:

            with transaction.atomic():

                # Lock and recheck products before completing the sale.
                locked_products = []

                for item in cart_items:

                    product = Product.objects.select_for_update().get(
                        id=item['product'].id
                    )

                    if item['quantity'] > product.stock_quantity:
                        messages.error(
                            request,
                            f'Not enough stock for {product.name}. '
                            f'Available stock: {product.stock_quantity}.'
                        )
                        return redirect('pos')

                    locked_products.append({
                        'product': product,
                        'quantity': item['quantity'],
                    })

                # Determine payment status.
                if amount_paid == grand_total:
                    payment_status = 'paid'
                elif amount_paid == 0:
                    payment_status = 'unpaid'
                else:
                    payment_status = 'partial'

                # Create invoice.
                invoice = Invoice.objects.create(
                    customer=customer,
                    customer_name=(
                        customer.name if customer else 'Walk-in Customer'
                    ),
                    subtotal=subtotal,
                    discount=discount,
                    total=grand_total,
                    payment_method=payment_method,
                    payment_status=payment_status,
                    amount_paid=amount_paid,
                )

                # Create invoice items and reduce stock.
                for locked_item in locked_products:

                    product = locked_item['product']
                    quantity = locked_item['quantity']

                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        product_name=product.name,
                        product_code=product.product_code,
                        quantity=quantity,
                        purchase_price=product.purchase_price,
                        unit_price=product.selling_price,
                        line_total=product.selling_price * quantity,
                    )

                    product.stock_quantity -= quantity

                    product.save(update_fields=['stock_quantity'])

        except Product.DoesNotExist:
            messages.error(
                request,
                'A product in your cart no longer exists. Please review your cart.'
            )
            return redirect('pos')

        # Clear cart only after the sale succeeds.
        request.session['cart'] = {}
        request.session['discount'] = '0.00'
        request.session['customer_id'] = None

        messages.success(
            request,
            f'Sale completed successfully! Invoice: {invoice.invoice_number}'
        )

        return redirect('invoice_detail', invoice_id=invoice.id)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'grand_total': grand_total,
        'customer': customer,
    }

    return render(request, 'billing/checkout.html', context)



def invoice_detail(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id
    )

    context = {
        'invoice': invoice,
        'invoice_items': invoice.items.all(),
    }

    return render(
        request,
        'billing/invoice_detail.html',
        context
    )
