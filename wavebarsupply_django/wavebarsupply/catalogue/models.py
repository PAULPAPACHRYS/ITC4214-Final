from django.db import models


class Category(models.Model):
    """A (category, sub-category) pair, e.g. ('non-alcohol', 'Soft Drinks').

    `name` keeps the same three choices and max length the old Product.category
    field had; `subcategory` keeps the old Product.subcategory max length.
    """

    CATEGORY_CHOICES = [
        ('non-alcohol', 'Non-Alcoholic'),
        ('fermented', 'Fermented'),
        ('distilled', 'Distilled'),
    ]

    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=50)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

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
    emoji = models.CharField(max_length=8)
    tags = models.JSONField(default=list)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name
