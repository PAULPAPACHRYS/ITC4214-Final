import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm

from accounts.forms import LOCATION_CHOICES
from accounts.models import Users
from catalogue.models import Brand, Category, Product, Subcategory
from likes.models import Like
from orders.models import Order, OrderItem


def _style(form):
    """Give every field the shared input class for consistent styling.

    Fields rendered as a drop-down get the select class instead, so the arrow
    and padding look right.
    """
    for field in form.fields.values():
        is_select = isinstance(field.widget, (forms.Select, forms.SelectMultiple))
        css = field.widget.attrs.get('class', '')
        extra = 'form_select' if is_select else 'form_input'
        field.widget.attrs['class'] = (css + ' ' + extra).strip()


def _image_choices():
    """The picture files that actually exist in static/images/.

    Turning the image field into a drop-down of real files means a sub-category
    can only ever point at a picture that is really there - a typed file name
    could easily be misspelled and would silently show no picture.
    """
    folder = settings.BASE_DIR / 'static' / 'images'
    allowed = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    try:
        files = sorted(f for f in os.listdir(folder)
                       if f.lower().endswith(allowed))
    except FileNotFoundError:
        files = []
    return [('', '--- no picture ---')] + [(f, f) for f in files]


class CategoryForm(forms.ModelForm):
    """A category is just its name, typed in freely.

    Unlike the other tables, nothing here points at another table, so there is
    nothing to pick from a list: a brand-new category is simply named. The name
    still has to be unique, so the same category cannot be added twice.
    """
    class Meta:
        model = Category
        fields = ['name']
        help_texts = {
            'name': 'e.g. non-alcohol. Must be unique.',
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)


class SubcategoryForm(forms.ModelForm):
    """A sub-category belongs to a category, chosen from a drop-down of the
    categories that exist, and shows a picture chosen from a drop-down of the
    files that exist in static/images/."""
    class Meta:
        model = Subcategory
        fields = ['name', 'category', 'image']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        # 'category' is a ForeignKey, so Django already renders it as a
        # drop-down listing the existing Category rows.
        self.fields['category'].empty_label = '--- choose a category ---'
        # 'image' is a plain text column, so give it a drop-down of real files.
        self.fields['image'] = forms.ChoiceField(
            choices=_image_choices(), required=False, label='Image')
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
        # Both fields are ForeignKeys, so both render as drop-downs.
        self.fields['product'].empty_label = '--- choose a product ---'
        self.fields['user'].empty_label = '--- choose a user ---'
        _style(self)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'brand', 'subcategory', 'price', 'volume', 'abv', 'tags']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        # brand and subcategory are ForeignKeys: Django renders both as
        # drop-downs of the existing rows.
        self.fields['brand'].empty_label = '--- choose a brand ---'
        self.fields['subcategory'].empty_label = '--- choose a sub-category ---'
        _style(self)


class OrderCreateForm(forms.ModelForm):
    """Adding an order: no status field, so a new order is always 'pending'."""
    class Meta:
        model = Order
        fields = ['user']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['user'].empty_label = '--- choose a user ---'
        _style(self)


class OrderEditForm(forms.ModelForm):
    """Editing an order: status can be changed (e.g. to completed / canceled)."""
    class Meta:
        model = Order
        fields = ['user', 'status']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        # user is a ForeignKey and status has fixed choices: both are drop-downs.
        self.fields['user'].empty_label = '--- choose a user ---'
        _style(self)


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity', 'unit_price']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['order'].empty_label = '--- choose an order ---'
        self.fields['product'].empty_label = '--- choose a product ---'
        _style(self)


# --- Users (admin only) ---

class UserEditForm(forms.ModelForm):
    """Edit an existing user, including their role. No password field here.

    bar_location uses the same fixed list of regions the registration form uses,
    so a user's location cannot be typed differently here than it is on sign-up.
    """

    bar_location = forms.ChoiceField(choices=LOCATION_CHOICES, required=False,
                                     label='Location / Region')

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
    bar_location = forms.ChoiceField(choices=LOCATION_CHOICES, required=False,
                                     label='Location / Region')

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'bar_name',
                  'bar_location', 'role']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)
