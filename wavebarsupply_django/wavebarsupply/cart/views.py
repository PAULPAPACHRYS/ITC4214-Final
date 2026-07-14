from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from catalogue.models import Product
from orders.models import Order, OrderItem

from .forms import AddToCartForm, CheckoutForm, RemoveCartForm, UpdateCartForm


def _get_cart(user):
    """Return the user's active cart: their single 'pending' Order."""
    order, _ = Order.objects.get_or_create(user=user, is_cart=True)
    return order


def _cart_total(order):
    total = Decimal('0.00')
    for item in order.items.all():
        total += item.quantity * item.unit_price
    return total


@login_required
def view_cart(request):
    order = Order.objects.filter(user=request.user, is_cart=True).first()
    items = [
        {
            'id': item.id,
            'image': item.product.image_url,
            'name': item.product.name,
            'unit_price': item.unit_price,
            'quantity': item.quantity,
            'line_total': item.quantity * item.unit_price,
        }
        for item in (order.items.select_related('product__subcategory') if order else [])
    ]
    checkout_form = CheckoutForm(initial={
        'name': request.user.get_full_name(),
        'phone': request.user.phone,
        'email': request.user.email,
        'address': ', '.join(p for p in [request.user.bar_name,
                                         request.user.bar_location] if p),
    })

    return render(request, 'cart/cart.html', {
        'items': items,
        'total': _cart_total(order) if order else 0,
        'checkout_form': checkout_form,
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
        order__user=request.user, order__is_cart=True,
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
        order__user=request.user, order__is_cart=True,
    )
    order = item.order
    item.delete()

    return JsonResponse({
        'ok': True,
        'cart_total': str(_cart_total(order)),
        'empty': not order.items.exists(),
    })


@login_required
@require_POST
def checkout(request):
    """Finalise the cart: record delivery details and mark the order completed.

    This only simulates payment; no card data is stored. Completing the pending
    order effectively empties the cart (the next visit starts a fresh one).
    """
    order = Order.objects.filter(user=request.user, is_cart=True).first()
    if order is None or not order.items.exists():
        return JsonResponse({'ok': False, 'error': 'Your cart is empty.'}, status=400)

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    data = form.cleaned_data
    order.delivery_name = data['name']
    order.delivery_address = data['address']
    order.delivery_phone = data['phone']
    order.delivery_email = data['email']
    order.is_cart = False       # no longer the cart
    order.status = 'pending'    # a newly placed order is pending
    order.save()

    return JsonResponse({'ok': True, 'order_number': order.id})
