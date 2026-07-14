from django.shortcuts import render
from catalogue.models import Brand, Category, Product, Subcategory
from catalogue.views import _products_as_dicts


def index(request):
    # A hand-picked, varied selection of products to feature on the homepage.
    featured_ids = [22, 39, 50, 28, 19, 1, 46, 43]
    products = _products_as_dicts(
        Product.objects.filter(id__in=featured_ids), user=request.user)

    # Preserve the order given in featured_ids (the DB returns them id-sorted).
    order = {pid: i for i, pid in enumerate(featured_ids)}
    products.sort(key=lambda p: order[p['id']])

    # Live counts for the stat cards, read straight from the database so the
    # numbers stay in sync with the catalogue instead of being hard-coded.
    # Now that sub-categories have their own table, both counts are simply the
    # number of rows in each table (no distinct() needed any more).
    return render(request, 'home/index.html', {
        'featured_products': products,
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'subcategory_count': Subcategory.objects.count(),
        'brand_count': Brand.objects.count(),
    })
