from django.db import models
from django.templatetags.static import static


class Category(models.Model):
    """A (category, sub-category) pair, e.g. ('non-alcohol', 'Soft Drinks').

    `name` keeps the same three choices and max length the old Product.category
    field had; `subcategory` keeps the old Product.subcategory max length.
    """

    CATEGORY_CHOICES = [
        ('non-alcohol', 'Non-Alcoholic'),
        ('fermented', 'Fermented'),
        ('distilled', 'Distilled'),
        ('cocktail', 'Cocktail Ingredients'),
        ('ice', 'Ice'),
        ('dairy', 'Dairy Products'),
        ('fresh', 'Fresh Products'),
        ('disposable', 'Disposable Products'),
        ('snacks', 'Bar Snacks'),
    ]

    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=50)

    # File name of the picture that represents this sub-category, e.g.
    # 'soft_drinks.jpg'. The file itself lives in static/images/, so only the
    # name is stored here and the folder is added by image_url() below.
    # Left blank until the picture is added; a blank value simply means the
    # product cards show an empty thumbnail instead of a broken image.
    image = models.CharField(
        max_length=100, blank=True, default='',
        help_text="File name inside static/images/, e.g. soft_drinks.jpg")

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    @property
    def image_url(self):
        """Full static path of the sub-category picture, or '' if none is set."""
        if self.image:
            return static(f'images/{self.image}')
        return ''

    def __str__(self):
        return f"{self.get_name_display()} · {self.subcategory}"


class Brand(models.Model):
    """`name` keeps the old Product.brand max length; `country` is new."""

    name = models.CharField(max_length=100)
    country = models.CharField(max_length=60)

    class Meta:
        db_table = 'brands'

    def __str__(self):
        return self.name


class Product(models.Model):
    """A single drink line. Category and brand now live in their own tables and
    are referenced here by foreign key (columns category_id and brand_id).
    """

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    volume = models.PositiveIntegerField(help_text='Volume in millilitres')
    abv = models.DecimalField(max_digits=4, decimal_places=1,
                              help_text='Alcohol by volume, %')
    tags = models.JSONField(default=list)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)

    class Meta:
        db_table = 'products'

    @property
    def image_url(self):
        """Picture shown on this product's card.

        A product does not own a picture: it inherits the one belonging to its
        sub-category, so every product in the same sub-category looks the same.
        Returns '' when the sub-category has no picture set yet.
        """
        return self.category.image_url

    def __str__(self):
        return self.name
