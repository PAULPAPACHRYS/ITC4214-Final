import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm

from accounts.forms import LOCATION_CHOICES
from accounts.models import Users
from catalogue.models import Brand, Category, Product, Subcategory, Tag
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


def _clean_text(value):
    """Tidy a typed-in string: trim the ends and collapse inner runs of spaces.

    Without this, 'Gin ' and 'Gin' and 'Gin  Tonic' are three different values as
    far as the database is concerned, which quietly defeats the duplicate checks.
    """
    return ' '.join((value or '').split())


def _no_duplicate(model, field, value, instance, message):
    """Reject a value that another row already has, ignoring case.

    The database's unique constraint is case-sensitive, so on its own it would
    happily accept both 'Bacardi' and 'bacardi'. This closes that gap.
    """
    if not value:
        return value
    clash = model.objects.filter(**{f'{field}__iexact': value})
    if instance and instance.pk:
        clash = clash.exclude(pk=instance.pk)
    if clash.exists():
        raise forms.ValidationError(message)
    return value


class ProductPriceSelect(forms.Select):
    """A product drop-down whose options carry the product's price.

    The price is put on each <option> as a data-price attribute, so the script
    can fill the unit price in as soon as a product is chosen (see
    static/js/database_form.js).
    """

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        product = getattr(value, 'instance', None)
        if product is not None:
            option['attrs']['data-price'] = str(product.price)
        return option


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
            'name': 'Lowercase letters and hyphens, e.g. non-alcohol. Must be unique.',
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)

    def clean_name(self):
        # The name doubles as a code in the Browse page filter (?cat=...), so it
        # is tidied into a slug: trimmed, lowercased, spaces turned into hyphens.
        # 'Soft Drinks' typed in here becomes 'soft-drinks'. The model's
        # slug_validator then rejects anything still not a valid slug.
        name = _clean_text(self.cleaned_data['name']).lower().replace(' ', '-')
        return _no_duplicate(Category, 'name', name, self.instance,
                             'A category with this name already exists.')


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

    def clean_name(self):
        return _clean_text(self.cleaned_data['name'])

    def clean(self):
        # A sub-category name only has to be unique WITHIN its category: two
        # categories may each have their own 'Mixers'.
        cleaned = super().clean()
        name, category = cleaned.get('name'), cleaned.get('category')
        if name and category:
            clash = Subcategory.objects.filter(category=category, name__iexact=name)
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                self.add_error('name',
                               'This category already has a sub-category with this name.')
        return cleaned


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'country']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)

    def clean_name(self):
        name = _clean_text(self.cleaned_data['name'])
        return _no_duplicate(Brand, 'name', name, self.instance,
                             'A brand with this name already exists.')

    def clean_country(self):
        return _clean_text(self.cleaned_data['country'])


class TagForm(forms.ModelForm):
    """Add or rename a tag. Tags are lowercase so the same word is one tag."""

    class Meta:
        model = Tag
        fields = ['name']
        help_texts = {'name': 'A single keyword, e.g. cola. Saved in lowercase.'}

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _style(self)

    def clean_name(self):
        name = _clean_text(self.cleaned_data['name']).lower()
        return _no_duplicate(Tag, 'name', name, self.instance,
                             'This tag already exists.')


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
        help_texts = {
            'price': 'Euro, greater than 0.',
            'volume': 'Millilitres, between 1 and 20000.',
            'abv': 'Alcohol by volume, between 0 and 100 %.',
            'tags': 'Pick from the tags that exist. To add a new one, use the Tags table.',
        }
        # The min/max/step below are the same limits the model validators
        # enforce. Putting them on the inputs means the browser blocks a bad
        # number before the form is even sent, while the model still checks it
        # on the server.
        widgets = {
            'price':  forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'volume': forms.NumberInput(attrs={'min': '1', 'max': '20000', 'step': '1'}),
            'abv':    forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.1'}),
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        # brand and subcategory are ForeignKeys: Django renders both as
        # drop-downs of the existing rows. tags is a many-to-many, so Django
        # renders it as a multiple-selection list of the tags that exist.
        self.fields['brand'].empty_label = '--- choose a brand ---'
        self.fields['subcategory'].empty_label = '--- choose a sub-category ---'
        self.fields['tags'].required = False
        # PositiveIntegerField puts min="0" on the input by itself, which would
        # let the browser accept a volume of 0 (the server would then reject it).
        # Setting it here keeps the two in step.
        self.fields['volume'].widget.attrs['min'] = '1'
        _style(self)

    def clean_name(self):
        return _clean_text(self.cleaned_data['name'])

    def clean(self):
        # The same drink, same brand, same size should not be added twice.
        cleaned = super().clean()
        name = cleaned.get('name')
        brand = cleaned.get('brand')
        volume = cleaned.get('volume')
        if name and brand and volume:
            clash = Product.objects.filter(
                name__iexact=name, brand=brand, volume=volume)
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                self.add_error(
                    'name',
                    'This product already exists for that brand and size.')
        return cleaned


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
        help_texts = {
            'unit_price': "Filled in from the product's price; change it only "
                          "if this line really is a different price.",
        }
        widgets = {
            # ProductPriceSelect puts each product's price on its <option>, which
            # is what lets the script fill the unit price in automatically.
            'product': ProductPriceSelect,
            'quantity': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'unit_price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['order'].empty_label = '--- choose an order ---'
        self.fields['product'].empty_label = '--- choose a product ---'
        # Same as volume above: PositiveIntegerField would otherwise put min="0"
        # on the input and let the browser accept an order line for 0 items.
        self.fields['quantity'].widget.attrs['min'] = '1'
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
