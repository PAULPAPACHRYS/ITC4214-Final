from django.shortcuts import render
from .models import Product


def _products_as_dicts(queryset):
    """Flatten Product rows (with their related category/brand) into the same
    shape the front-end JavaScript already expects.

    - brand / category / subcategory come from the related tables.
    - volume is turned back into a display string (e.g. 330 -> "330ml").
    - price and abv are cast to float so the JSON carries numbers, not strings.
    """
    products = []
    for p in queryset.select_related('category', 'brand'):
        products.append({
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name,
            'category': p.category.name,
            'subcategory': p.category.subcategory,
            'price': float(p.price),
            'volume': f"{p.volume}ml",
            'abv': float(p.abv),
            'emoji': p.emoji,
            'tags': p.tags,
        })
    return products


def browse(request):
    products = _products_as_dicts(Product.objects.all())
    return render(request, 'catalogue/browse.html', {'products': products})
