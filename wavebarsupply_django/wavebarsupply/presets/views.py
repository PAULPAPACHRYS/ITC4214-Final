from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from orders.models import Order, OrderItem
from .forms import PresetForm
from .models import Preset


@login_required
@require_POST
def create(request):
    # ceate a preset owned by the currently logged in user
    form = PresetForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    preset = form.save(commit=False)
    preset.user = request.user
    preset.save()
    form.save_m2m()   #attach chosen ingredients

    return JsonResponse({'ok': True, 'preset': preset.to_dict()})


@login_required
@require_POST
def edit(request, preset_id):
    # update one of the currently logged in user's own presets
    preset = get_object_or_404(Preset, pk=preset_id, user=request.user)
    form = PresetForm(request.POST, instance=preset)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    form.save()
    return JsonResponse({'ok': True, 'preset': preset.to_dict()})


@login_required
@require_POST
def delete(request, preset_id):
    # delete one of the currently logged in user's own presets
    preset = get_object_or_404(Preset, pk=preset_id, user=request.user)
    preset.delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def add_to_cart(request):
    # add every ingredient of a preset to the cart, quantity same as servings
    preset = get_object_or_404(Preset, pk=request.POST.get('preset_id'))

    # a user can only use the default presets or their own.
    if preset.user_id not in (None, request.user.id):
        return JsonResponse({'ok': False}, status=404)

    try:
        servings = int(request.POST.get('servings', 1))
    except (TypeError, ValueError):
        servings = 1
    servings = max(servings, 1)

    order, _ = Order.objects.get_or_create(user=request.user, is_cart=True)
    for product in preset.ingredients.all():
        item, created = OrderItem.objects.get_or_create(
            order=order, product=product,
            defaults={'quantity': servings, 'unit_price': product.price})
        if not created:
            item.quantity += servings
            item.save()

    total = sum(i.quantity * i.unit_price for i in order.items.all())
    return JsonResponse({'ok': True, 'servings': servings, 'cart_total': str(total)})
