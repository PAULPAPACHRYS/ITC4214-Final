from django.shortcuts import render
from catalogue.models import Brand, Category, Product, Subcategory
from catalogue.views import _products_as_dicts


def index(request):
    """
    display the 10 most recently added products, the id is auto-incremented, 
    so ordering by -id and taking 10 gives the latest products, newest first
    """
    latest = Product.objects.order_by('-id')[:10]
    products = _products_as_dicts(latest, user=request.user)

    #apply again the newest-first order for display
    products.sort(key=lambda p: p['id'], reverse=True)

    return render(request, 'home/index.html', {
        'latest_products': products,
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'subcategory_count': Subcategory.objects.count(),
        'brand_count': Brand.objects.count(),
    })
