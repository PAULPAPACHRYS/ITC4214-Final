from functools import wraps

from django.contrib import messages
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Users
from catalogue.models import Brand, Category, Product, Subcategory, Tag
from likes.models import Like
from orders.models import Order, OrderItem

from . import forms

def _objects(config):
    """Rows for a table: use its custom queryset if it has one, else all rows."""
    getter = config.get('queryset')
    return getter() if getter else config['model'].objects.all()


# Registry of the tables managed on the Database page.
#   columns    -> fields shown in the list view
#   form       -> ModelForm used to edit (and add, unless add_form is given)
#   admin_only -> table is only visible/editable by admins (the Users table)
TABLES = {
    'categories':  {'model': Category,  'label': 'Categories',  'admin_only': False,
                    'columns': ['id', 'name'],
                    'form': forms.CategoryForm},
    'subcategories': {'model': Subcategory, 'label': 'Sub-categories', 'admin_only': False,
                      'columns': ['id', 'name', 'category', 'image'],
                      'form': forms.SubcategoryForm},
    'tags':        {'model': Tag,       'label': 'Tags',        'admin_only': False,
                    'columns': ['id', 'name'],
                    'form': forms.TagForm},
    'brands':      {'model': Brand,     'label': 'Brands',      'admin_only': False,
                    'columns': ['id', 'name', 'country'],
                    'form': forms.BrandForm},
    'products':    {'model': Product,   'label': 'Products',    'admin_only': False,
                    'columns': ['id', 'name', 'brand', 'subcategory', 'price', 'volume', 'abv'],
                    'form': forms.ProductForm},
    'orders':      {'model': Order,     'label': 'Orders',      'admin_only': False,
                    'columns': ['id', 'user', 'order_date', 'status'],
                    'form': forms.OrderEditForm, 'add_form': forms.OrderCreateForm,
                    'queryset': lambda: Order.objects.filter(is_cart=False)},
    'order_items': {'model': OrderItem, 'label': 'Order Items', 'admin_only': False,
                    'columns': ['id', 'order', 'product', 'quantity', 'unit_price'],
                    'form': forms.OrderItemForm},
    'likes':       {'model': Like,      'label': 'Likes',       'admin_only': False,
                    'columns': ['id', 'product', 'user'],
                    'form': forms.LikeForm},
    'users':       {'model': Users,     'label': 'Users',       'admin_only': True,
                    'columns': ['id', 'first_name', 'last_name', 'email', 'role', 'bar_name', 'bar_location'],
                    'form': forms.UserEditForm, 'add_form': forms.UserCreateForm},
}


def staff_required(view):
    """Allow only logged-in employees and admins."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('accounts:login')
        if user.role not in ('employee', 'admin'):
            return redirect('home:index')
        return view(request, *args, **kwargs)
    return wrapper


def _get_config(request, key):
    """Return the table config, or None if it doesn't exist / isn't allowed."""
    config = TABLES.get(key)
    if config is None:
        return None
    if config['admin_only'] and request.user.role != 'admin':
        return None
    return config


@staff_required
def home(request):
    is_admin = request.user.role == 'admin'
    tables = [
        {'key': key, 'label': cfg['label'], 'count': _objects(cfg).count()}
        for key, cfg in TABLES.items()
        if not cfg['admin_only'] or is_admin
    ]
    return render(request, 'database/home.html', {'tables': tables})


@staff_required
def table(request, key):
    config = _get_config(request, key)
    if config is None:
        raise Http404
    columns = config['columns']
    rows = [
        {'pk': obj.pk, 'cells': [getattr(obj, col) for col in columns]}
        for obj in _objects(config)
    ]
    return render(request, 'database/table.html', {
        'key': key, 'label': config['label'], 'columns': columns, 'rows': rows,
    })


@staff_required
def add(request, key):
    config = _get_config(request, key)
    if config is None:
        raise Http404
    form_class = config.get('add_form', config['form'])
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"{config['label']} entry added.")
            return redirect('database:table', key=key)
    else:
        form = form_class()
    return render(request, 'database/form.html', {
        'form': form, 'key': key, 'label': config['label'], 'mode': 'Add',
    })


@staff_required
def edit(request, key, pk):
    config = _get_config(request, key)
    if config is None:
        raise Http404
    obj = get_object_or_404(config['model'], pk=pk)
    if request.method == 'POST':
        form = config['form'](request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{config['label']} entry updated.")
            return redirect('database:table', key=key)
    else:
        form = config['form'](instance=obj)
    return render(request, 'database/form.html', {
        'form': form, 'key': key, 'label': config['label'], 'mode': 'Edit',
    })


@staff_required
def delete(request, key, pk):
    config = _get_config(request, key)
    if config is None:
        raise Http404
    obj = get_object_or_404(config['model'], pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, f"{config['label']} entry deleted.")
        except ProtectedError:
            messages.error(request,
                           "Can't delete this entry because other records depend on it.")
    return redirect('database:table', key=key)
