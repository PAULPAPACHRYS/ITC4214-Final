from django.shortcuts import render
from catalogue.models import Product
from catalogue.views import _products_as_dicts


def index(request):
    # A hand-picked, varied selection of products to feature on the homepage.
    featured_ids = [22, 39, 50, 28, 19, 1, 46, 43]
    products = _products_as_dicts(Product.objects.filter(id__in=featured_ids))

    # Preserve the order given in featured_ids (the DB returns them id-sorted).
    order = {pid: i for i, pid in enumerate(featured_ids)}
    products.sort(key=lambda p: order[p['id']])

    return render(request, 'home/index.html', {'featured_products': products})
