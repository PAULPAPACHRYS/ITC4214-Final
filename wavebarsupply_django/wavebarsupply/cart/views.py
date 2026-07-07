from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from catalogue.models import Product
from orders.models import Order, OrderItem

from .forms import AddToCartForm, RemoveCartForm, UpdateCartForm


def _get_cart(user):
    """Return the user's active cart: their single 'pending' Order."""
    order, _ = Order.objects.get_or_create(user=user, status='pending')
    return order


def _cart_total(order):
    total = Decimal('0.00')
    for item in order.items.all():
        total += item.quantity * item.unit_price
    return total


@login_required
def view_cart(request):
    order = _get_cart(request.user)
    items = [
        {
            'id': item.id,
            'emoji': item.product.emoji,
            'name': item.product.name,
            'unit_price': item.unit_price,
            'quantity': item.quantity,
            'line_total': item.quantity * item.unit_price,
        }
        for item in order.items.select_related('product')
    ]
    return render(request, 'cart/cart.html', {
        'items': items,
        'total': _cart_total(order),
    })


@login_required
@require_POST
def add(request):
    form = AddToCartForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False}, status=400)

    product = get_object_or_404(Product, pk=form.cleaned_data['product_id'])
    quantity = form.cleaned_data['quantity']
    order = _get_cart(request.user)

    item, created = OrderItem.objects.get_or_create(
        order=order, product=product,
        defaults={'quantity': quantity, 'unit_price': product.price},
    )
    if not created:
        item.quantity += quantity
        item.save()

    return JsonResponse({'ok': True, 'cart_total': str(_cart_total(order))})


@login_required
@require_POST
def update(request):
    form = UpdateCartForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False}, status=400)

    item = get_object_or_404(
        OrderItem, pk=form.cleaned_data['item_id'],
        order__user=request.user, order__status='pending',
    )
    item.quantity = form.cleaned_data['quantity']
    item.save()

    return JsonResponse({
        'ok': True,
        'quantity': item.quantity,
        'line_total': str(item.quantity * item.unit_price),
        'cart_total': str(_cart_total(item.order)),
    })


@login_required
@require_POST
def remove(request):
    form = RemoveCartForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False}, status=400)

    item = get_object_or_404(
        OrderItem, pk=form.cleaned_data['item_id'],
        order__user=request.user, order__status='pending',
    )
    order = item.order
    item.delete()

    return JsonResponse({
        'ok': True,
        'cart_total': str(_cart_total(order)),
        'empty': not order.items.exists(),
    })
