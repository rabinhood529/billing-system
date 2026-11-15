from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos, name='pos'),

    path(
        'add-to-cart/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'remove-from-cart/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'update-cart/<int:product_id>/',
        views.update_cart,
        name='update_cart'
    ),

    path(
        'update-discount/',
        views.update_discount,
        name='update_discount'
    ),


    path(
    'update-customer/',
    views.update_customer,
    name='update_customer'
),
path(
    'checkout/',
    views.checkout,
    name='checkout'
),

path(
    'invoice/<int:invoice_id>/',
    views.invoice_detail,
    name='invoice_detail'
),
path(
    'invoices/',
    views.invoice_list,
    name='invoice_list'
),

path(
    'reports/',
    views.sales_report,
    name='sales_report'
),
]