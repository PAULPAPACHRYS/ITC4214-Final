from decimal import Decimal

from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.templatetags.static import static

# A category name is used as a code (it appears in the browse filter, e.g.
# ?cat=non-alcohol), so it must be a slug: lowercase letters joined by hyphens.
slug_validator = RegexValidator(
    regex=r'^[a-z]+(-[a-z]+)*$',
    message='Use lowercase letters and hyphens only, e.g. non-alcohol.')


class Category(models.Model):
    """A top-level category, e.g. 'non-alcohol'.

    A category now holds nothing but its own name. The sub-categories that
    belong to it live in their own table (see Subcategory below) and point back
    here with a foreign key.
    """

    # Nice display labels for the categories that came with the site. The name
    # field is NOT limited to these: a new category can simply be typed in on
    # the Database page. Anything not listed here is shown as it was typed.
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

    # unique: the same category can only appear once in the table.
    # No `choices` here, so the name is typed in freely when adding a category,
    # but it must still be a valid slug (see slug_validator above).
    name = models.CharField(max_length=20, unique=True,
                            validators=[slug_validator])

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    @property
    def display_name(self):
        """The label to show for this category.

        Known categories get their tidy label ('non-alcohol' -> 'Non-Alcoholic');
        a newly added one is tidied up from its slug ('soft-drinks' -> 'Soft
        Drinks'), so it reads properly on the Browse page tabs.
        """
        if self.name in self.CATEGORY_LABELS:
            return self.CATEGORY_LABELS[self.name]
        return self.name.replace('-', ' ').title()

    def __str__(self):
        return self.display_name


class Subcategory(models.Model):
    """A sub-category, e.g. 'Soft Drinks', belonging to exactly one Category.

    This used to be a plain text column on Category. It is now its own table
    with a foreign key (column category_id) to the category it belongs to, so a
    sub-category can never name a category that does not exist.

    The picture representing the sub-category lives here too, because the
    picture belongs to the sub-category and every product in it shares it.
    """

    name = models.CharField(max_length=50)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='subcategories')

    # File name of the picture, e.g. 'soft_drinks.jpg'. The file itself lives in
    # static/images/, so only the name is stored here and the folder is added by
    # image_url() below.
    image = models.CharField(
        max_length=100, blank=True, default='',
        help_text="File name inside static/images/, e.g. soft_drinks.jpg")

    class Meta:
        db_table = 'subcategories'
        verbose_name_plural = 'subcategories'
        constraints = [
            # The same sub-category name cannot be added twice under the same
            # category (two different categories may both have e.g. 'Mixers').
            models.UniqueConstraint(fields=['category', 'name'],
                                    name='unique_subcategory_per_category'),
        ]

    @property
    def image_url(self):
        """Full static path of the sub-category picture, or '' if none is set."""
        if self.image:
            return static(f'images/{self.image}')
        return ''

    def __str__(self):
        return f"{self.category.display_name} · {self.name}"


class Tag(models.Model):
    """A keyword that can be attached to products, e.g. 'cola' or 'citrus'.

    Tags used to be free text typed into each product, which meant the same idea
    could be spelled three different ways ('cola', 'Cola', 'colaa') without any
    warning. They are now rows in their own table, so a product picks the tags it
    wants from the list, and a new tag is added once, deliberately.
    """

    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    """`name` keeps the old Product.brand max length; `country` is new."""

    # unique: the same brand cannot be entered twice.
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=60)

    class Meta:
        db_table = 'brands'

    def __str__(self):
        return self.name


class Product(models.Model):
    """A single drink line.

    A product points at a sub-category (column subcategory_id) and reaches its
    category through it:  product -> subcategory -> category.
    """

    name = models.CharField(max_length=100)
    # The validators below stop nonsense numbers being saved: a price must be
    # positive, a volume must be a sensible number of millilitres, and alcohol
    # by volume can only be a percentage (0-100).
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
            # The same drink, from the same brand, in the same size, should only
            # exist once. (The same name in a different size is a real product,
            # so volume is part of the check.)
            models.UniqueConstraint(fields=['name', 'brand', 'volume'],
                                    name='unique_product_name_brand_volume'),
        ]

    @property
    def category(self):
        """The product's category, reached through its sub-category."""
        return self.subcategory.category

    @property
    def image_url(self):
        """Picture shown on this product's card.

        A product does not own a picture: it inherits the one belonging to its
        sub-category, so every product in the same sub-category looks the same.
        Returns '' when the sub-category has no picture set yet.
        """
        return self.subcategory.image_url

    def __str__(self):
        return self.name
