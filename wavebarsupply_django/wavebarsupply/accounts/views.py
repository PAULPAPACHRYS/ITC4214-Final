from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalogue.models import Product
from orders.models import Order
from presets.models import Preset
from presets.forms import PresetForm
from .forms import AccountEditForm, LoginForm, RegisterForm


def auth_view(request):
    """Login + register page (for guests). Logged-in users are sent to Account."""
    if request.user.is_authenticated:
        return redirect('accounts:account')

    login_form = LoginForm(request)
    register_form = RegisterForm()
    active_panel = 'login'

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            active_panel = 'login'
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('catalogue:browse')

        elif 'register_submit' in request.POST:
            register_form = RegisterForm(request.POST)
            active_panel = 'register'
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('catalogue:browse')

    return render(request, 'accounts/login.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_panel': active_panel,
    })


@login_required
def account(request):
    """Shows the logged-in user's details and lets them edit them."""
    show_edit = False
    if request.method == 'POST':
        form = AccountEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:account')
        show_edit = True          # keep the edit form open to show errors
    else:
        form = AccountEditForm(instance=request.user)

    # Dashboard data for the right-hand side of the page.
    orders = (Order.objects
              .filter(user=request.user, is_cart=False)
              .prefetch_related('items__product')
              .order_by('-order_date', '-id'))
    my_presets = list(Preset.objects
                      .filter(user=request.user)
                      .prefetch_related('ingredients'))
    liked_products = (Product.objects
                      .filter(likes__user=request.user)
                      .select_related('brand', 'category'))

    # Extra data the edit-preset overlay needs (product search + prefill).
    presets_json = [{**p.to_dict(), 'owned': True} for p in my_presets]
    products_json = [{'id': p.id, 'name': p.name,
                      'brand': p.brand.name, 'subcategory': p.category.subcategory}
                     for p in Product.objects.select_related('brand', 'category')]

    return render(request, 'accounts/account.html', {
        'form': form,
        'show_edit': show_edit,
        'orders': orders,
        'my_presets': my_presets,
        'liked_products': liked_products,
        'preset_form': PresetForm(),
        'presets_json': presets_json,
        'products_json': products_json,
    })


def logout_view(request):
    logout(request)
    return redirect('home:index')
