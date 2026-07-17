from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from catalogue.models import Product
from .models import Like


@require_POST
def toggle(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'auth'}, status=403)

    product = get_object_or_404(Product, pk=request.POST.get('product_id'))

    like, created = Like.objects.get_or_create(product=product, user=request.user)
    if created:
        # the row was new, the user just liked it
        liked = True
    else:
        # the row existed, clicking again unlikes it
        like.delete()
        liked = False

    return JsonResponse({'ok': True, 'liked': liked, 'count': product.likes.count()})
