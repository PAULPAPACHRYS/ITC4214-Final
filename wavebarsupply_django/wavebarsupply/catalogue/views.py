from django.shortcuts import render
from .models import Product


def _products_as_dicts(queryset):
    """Turn Product rows into plain dicts the front-end JS can read as JSON.

    price is cast to float so JavaScript receives a number (DecimalField would
    otherwise be serialised as a string and break product.price.toFixed()).
    """
    products = list(queryset.values(
        'id', 'name', 'brand', 'category', 'subcategory',
        'price', 'volume', 'abv', 'emoji', 'tags',
    ))
    for p in products:
        p['price'] = float(p['price'])
    return products


def browse(request):
    products = _products_as_dicts(Product.objects.all())
    return render(request, 'catalogue/browse.html', {'products': products})
