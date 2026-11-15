
from django.shortcuts import render, redirect, get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Customer
import re


def validate_customer_data(request, customer=None):

    errors = {}

    name = request.POST.get('name', '').strip()
    phone_input = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    address = request.POST.get('address', '').strip()

    form_data = {
        'name': name,
        'phone': phone_input,
        'email': email,
        'address': address,
    }

    # 1. Validate customer name
    if len(name) < 2:
        errors['name'] = 'Customer name must contain at least 2 characters.'

    elif name.isdigit():
        errors['name'] = 'Customer name cannot contain only numbers.'

    elif len(name) > 200:
        errors['name'] = 'Customer name cannot exceed 200 characters.'

    # 2. Normalize phone number
    phone = re.sub(r'[\s()-]', '', phone_input)

    if phone.startswith('+977'):
        phone = phone[4:]

    elif phone.startswith('977') and len(phone) == 13:
        phone = phone[3:]

    # 3. Validate Nepal mobile number
    pattern = r'^(974|975|976|984|985|986|970|971|980|981|982)\d{7}$'

    if not phone:
        errors['phone'] = 'Phone number is required.'

    elif not re.fullmatch(pattern, phone):
        errors['phone'] = (
            'Enter a valid Nepal mobile number. '
            'Example: 9800000001 or +9779800000001.'
        )

    else:

        # Check duplicate phone number
        duplicate_numbers = Customer.objects.filter(phone=phone)

        if customer:
            duplicate_numbers = duplicate_numbers.exclude(
                id=customer.id
            )

        if duplicate_numbers.exists():
            errors['phone'] = 'This phone number already exists.'

    # 4. Validate email (optional)
    if email:

        if len(email) > 254:
            errors['email'] = 'Email cannot exceed 254 characters.'

        else:
            try:
                validate_email(email)

            except ValidationError:
                errors['email'] = 'Enter a valid email address.'

    # 5. Address is optional

    values = {
        'name': name,
        'phone': phone,
        'email': email,
        'address': address,
    }

    return form_data, errors, values


def customer_list(request):

    search_query = request.GET.get('search', '')

    customers = Customer.objects.all()

    if search_query:
        customers = customers.filter(
            name__icontains=search_query
        ) | customers.filter(
            phone__icontains=search_query
        ) | customers.filter(
            email__icontains=search_query
        )

    context = {
        'customers': customers,
        'search_query': search_query
    }

    return render(
        request,
        'customers/customer_list.html',
        context
    )


def customer_create(request):

    form_data = {}
    errors = {}

    if request.method == 'POST':

        form_data, errors, values = validate_customer_data(request)

        if not errors:

            Customer.objects.create(**values)

            return redirect('customer_list')

    return render(
        request,
        'customers/customer_form.html',
        {
            'form_data': form_data,
            'errors': errors
        }
    )


def customer_edit(request, customer_id):

    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':

        form_data, errors, values = validate_customer_data(
            request,
            customer
        )

        if not errors:

            for field, value in values.items():
                setattr(customer, field, value)

            customer.save()

            return redirect('customer_list')

    else:

        form_data = {
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address,
        }

        errors = {}

    return render(
        request,
        'customers/customer_form.html',
        {
            'customer': customer,
            'form_data': form_data,
            'errors': errors
        }
    )


def customer_delete(request, customer_id):

    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':

        customer.delete()

        return redirect('customer_list')

    return render(
        request,
        'customers/customer_confirm_delete.html',
        {
            'customer': customer
        }
    )
