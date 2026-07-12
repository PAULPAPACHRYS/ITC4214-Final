from django.shortcuts import render
from catalogue.models import Brand, Category, Product
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
    # Categories are the distinct top-level names; sub-categories are the
    # distinct subcategory values on the Category table.
    category_count = (Category.objects
                      .values('name').distinct().count())
    subcategory_count = (Category.objects
                         .values('subcategory').distinct().count())

    return render(request, 'home/index.html', {
        'featured_products': products,
        'product_count': Product.objects.count(),
        'category_count': category_count,
        'subcategory_count': subcategory_count,
        'brand_count': Brand.objects.count(),
    })
