from django.shortcuts import render
from catalogue.models import Brand, Category, Product, Subcategory
from catalogue.views import _products_as_dicts


def index(request):
    # The 10 most recently added products. There is no "date added" column, but
    # the id is auto-incremented, so the highest ids are the newest rows -
    # ordering by -id and taking 10 gives the latest products, newest first.
    latest = Product.objects.order_by('-id')[:10]
    products = _products_as_dicts(latest, user=request.user)

    # _products_as_dicts returns them id-sorted (ascending), so re-apply the
    # newest-first order for display.
    products.sort(key=lambda p: p['id'], reverse=True)

    # Live counts for the stat cards, read straight from the database so the
    # numbers stay in sync with the catalogue instead of being hard-coded.
    # Now that sub-categories have their own table, both counts are simply the
    # number of rows in each table (no distinct() needed any more).
    return render(request, 'home/index.html', {
        'latest_products': products,
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'subcategory_count': Subcategory.objects.count(),
        'brand_count': Brand.objects.count(),
    })
