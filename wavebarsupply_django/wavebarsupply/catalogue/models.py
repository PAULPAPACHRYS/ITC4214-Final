from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.templatetags.static import static

slug_validator = RegexValidator(
    regex=r'^[a-z]+(-[a-z]+)*$',
    message='Use lowercase letters and hyphens only, e.g. non-alcohol.')

class Category(models.Model):
    CATEGORY_LABELS = {
        'non-alcohol': 'Non-Alcoholic',
        'fermented': 'Fermented',
        'distilled': 'Distilled',
        'cocktail': 'Cocktail Ingredients',
        'ice': 'Ice',
        'dairy': 'Dairy Products',
        'fresh': 'Fresh Products',
        'disposable': 'Disposable Products',
        'snacks': 'Bar Snacks',
    }

    name = models.CharField(max_length=20, unique=True,
                            validators=[slug_validator])

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    @property
    def display_name(self):
        if self.name in self.CATEGORY_LABELS:
            return self.CATEGORY_LABELS[self.name]
        return self.name.replace('-', ' ').title()

    def __str__(self):
        return self.display_name


class Subcategory(models.Model):

    name = models.CharField(max_length=50)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='subcategories')

    image = models.CharField(
        max_length=100, blank=True, default='',
        help_text="File name inside static/images/, e.g. soft_drinks.jpg")

    class Meta:
        db_table = 'subcategories'
        verbose_name_plural = 'subcategories'
        constraints = [
            models.UniqueConstraint(fields=['category', 'name'],
                                    name='unique_subcategory_per_category'),
        ]

    @property
    def image_url(self):
        if self.image:
            return static(f'images/{self.image}')
        return ''

    def __str__(self):
        return f"{self.category.display_name} · {self.name}"


class Tag(models.Model):

    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=60)

    class Meta:
        db_table = 'brands'

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    volume = models.PositiveIntegerField(
        help_text='Volume in millilitres',
        validators=[MinValueValidator(1), MaxValueValidator(20000)])
    abv = models.DecimalField(
        max_digits=4, decimal_places=1, help_text='Alcohol by volume, %',
        validators=[MinValueValidator(Decimal('0')),
                    MaxValueValidator(Decimal('100'))])
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)

    class Meta:
        db_table = 'products'
        constraints = [
            models.UniqueConstraint(fields=['name', 'brand', 'volume'],
                                    name='unique_product_name_brand_volume'),
        ]

    @property
    def category(self):
        return self.subcategory.category

    @property
    def image_url(self):
        return self.subcategory.image_url

    def __str__(self):
        return self.name
