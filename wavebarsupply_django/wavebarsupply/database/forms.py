from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Users
from catalogue.models import Brand, Category, Product
from likes.models import Like
from orders.models import Order, OrderItem


def _style(form):
    """Give every field the shared input class for consistent styling."""
    for field in form.fields.values():
        css = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = (css + ' form_input').strip()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'subcategory']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'country']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ['product', 'user']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'category', 'price', 'volume', 'abv', 'emoji', 'tags']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class OrderCreateForm(forms.ModelForm):
    """Adding an order: no status field, so a new order is always 'pending'."""
    class Meta:
        model = Order
        fields = ['user']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class OrderEditForm(forms.ModelForm):
    """Editing an order: status can be changed (e.g. to completed / canceled)."""
    class Meta:
        model = Order
        fields = ['user', 'status']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity', 'unit_price']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


# --- Users (admin only) ---

class UserEditForm(forms.ModelForm):
    """Edit an existing user, including their role. No password field here."""

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'bar_name',
                  'bar_location', 'role', 'is_active']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class UserCreateForm(UserCreationForm):
    """Add a new user (built-in UserCreationForm) with a chosen role."""

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=20, required=False)
    bar_name = forms.CharField(max_length=100, required=False)
    bar_location = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'bar_name',
                  'bar_location', 'role']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)
