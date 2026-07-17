import os
import re
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from accounts.forms import LOCATION_CHOICES, UserFieldsMixin
from accounts.validators import name_validator, phone_validator
from accounts.models import Users
from catalogue.models import Brand, Category, Product, Subcategory, Tag
from likes.models import Like
from orders.models import Order, OrderItem


def _style(form):
    for field in form.fields.values():
        is_select = isinstance(field.widget, (forms.Select, forms.SelectMultiple))
        css = field.widget.attrs.get('class', '')
        extra = 'form_select' if is_select else 'form_input'
        field.widget.attrs['class'] = (css + ' ' + extra).strip()


def _clean_text(value):
    return ' '.join((value or '').split())


def _no_duplicate(model, field, value, instance, message):
    if not value:
        return value
    clash = model.objects.filter(**{f'{field}__iexact': value})
    if instance and instance.pk:
        clash = clash.exclude(pk=instance.pk)
    if clash.exists():
        raise forms.ValidationError(message)
    return value


class ProductPriceSelect(forms.Select):
    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        product = getattr(value, 'instance', None)
        if product is not None:
            option['attrs']['data-price'] = str(product.price)
        return option


def _images_dir():
    folder = settings.BASE_DIR / 'static' / 'images'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _save_uploaded_image(upload):
    base = os.path.basename(upload.name)
    stem, ext = os.path.splitext(base)
    stem = re.sub(r'[^A-Za-z0-9._-]', '_', stem) or 'image'
    ext = ext.lower()

    folder = _images_dir()
    filename = f'{stem}{ext}'
    counter = 1
    while (folder / filename).exists():
        filename = f'{stem}_{counter}{ext}'
        counter += 1

    with open(folder / filename, 'wb') as destination:
        for chunk in upload.chunks(): #chunk handles larger files
            destination.write(chunk)
    return filename


def _image_choices():
    folder = settings.BASE_DIR / 'static' / 'images'
    allowed = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    try:
        files = sorted(f for f in os.listdir(folder)
                       if f.lower().endswith(allowed))
    except FileNotFoundError:
        files = []
    return [('', '--- no picture ---')] + [(f, f) for f in files]


class CategoryForm(forms.ModelForm):
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
        name = _clean_text(self.cleaned_data['name']).lower().replace(' ', '-')
        return _no_duplicate(Category, 'name', name, self.instance,
                             'A category with this name already exists.')


class SubcategoryForm(forms.ModelForm):
    upload = forms.FileField(
        required=False, label='...or upload a new picture',
        help_text='Choose an image file to add it to the library and use it here.')

    class Meta:
        model = Subcategory
        fields = ['name', 'category', 'image']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['category'].empty_label = '--- choose a category ---'
        self.fields['image'] = forms.ChoiceField(
            choices=_image_choices(), required=False, label='Image')
        _style(self)

    def clean_name(self):
        return _clean_text(self.cleaned_data['name'])

    def clean_upload(self):
        upload = self.cleaned_data.get('upload')
        if not upload:
            return upload
        allowed = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        ext = os.path.splitext(upload.name)[1].lower()
        if ext not in allowed:
            raise forms.ValidationError(
                'Please upload an image file (jpg, png, webp or gif).')
        if upload.size > 5 * 1024 * 1024: # 5 MB
            raise forms.ValidationError('Please keep the image under 5 MB.')
        return upload

    def clean(self):
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

    def save(self, commit=True):
        upload = self.cleaned_data.get('upload')
        if upload:
            filename = _save_uploaded_image(upload)
            self.instance.image = filename
        return super().save(commit=commit)


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

        widgets = {
            'price':  forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'volume': forms.NumberInput(attrs={'min': '1', 'max': '20000', 'step': '1'}),
            'abv':    forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.1'}),
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['brand'].empty_label = '--- choose a brand ---'
        self.fields['subcategory'].empty_label = '--- choose a sub-category ---'
        self.fields['tags'].required = False
        self.fields['volume'].widget.attrs['min'] = '1'
        _style(self)

    def clean_name(self):
        return _clean_text(self.cleaned_data['name'])

    def clean(self):
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
    class Meta:
        model = Order
        fields = ['user']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['user'].empty_label = '--- choose a user ---'
        _style(self)


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'status']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
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
            'product': ProductPriceSelect,
            'quantity': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'unit_price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['order'].empty_label = '--- choose an order ---'
        self.fields['product'].empty_label = '--- choose a product ---'
        self.fields['quantity'].widget.attrs['min'] = '1'
        _style(self)


# users edit form, only available for admins
class UserEditForm(UserFieldsMixin, forms.ModelForm):
    bar_location = forms.ChoiceField(choices=LOCATION_CHOICES, required=False,
                                     label='Location / Region')

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'bar_name',
                  'bar_location', 'role', 'is_active']
        help_texts = {'phone': 'e.g. +30 6900 111111'}

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.apply_field_hints()
        _style(self)


class UserCreateForm(UserFieldsMixin, UserCreationForm):
    first_name = forms.CharField(max_length=50, validators=[name_validator])
    last_name = forms.CharField(max_length=50, validators=[name_validator])
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=20, required=False,
                            validators=[phone_validator],
                            help_text='e.g. +30 6900 111111')
    bar_name = forms.CharField(max_length=100, required=False)
    bar_location = forms.ChoiceField(choices=LOCATION_CHOICES, required=False,
                                     label='Location / Region')

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'bar_name',
                  'bar_location', 'role']

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.apply_field_hints()
        _style(self)
