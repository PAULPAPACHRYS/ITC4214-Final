from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from catalogue.models import Product
from .models import Like


@require_POST
def toggle(request):
    """Toggle the current user's like for a product (AJAX endpoint).

    POST body: product_id. Returns JSON: {ok, liked, count}
      - liked -> whether the user now likes the product (after the toggle)
      - count -> the product's new total like count
    Only logged-in users may like; anonymous requests get a 403 JSON response.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'auth'}, status=403)

    product = get_object_or_404(Product, pk=request.POST.get('product_id'))

    like, created = Like.objects.get_or_create(product=product, user=request.user)
    if created:
        liked = True            # the row was new -> the user just liked it
    else:
        like.delete()           # the row existed -> clicking again unlikes it
        liked = False

    return JsonResponse({'ok': True, 'liked': liked, 'count': product.likes.count()})
