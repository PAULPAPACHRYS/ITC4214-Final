from django.db import models


class Product(models.Model):
    """A single drink/beverage line in the WaveBar catalogue."""

    CATEGORY_CHOICES = [
        ('non-alcohol', 'Non-Alcoholic'),
        ('fermented', 'Fermented'),
        ('distilled', 'Distilled'),
    ]
    ABV_CHOICES = [
        ('none', 'Non-Alcoholic (0%)'),
        ('low', 'Low (under 8%)'),
        ('medium', 'Medium (8-20%)'),
        ('high', 'High (20%+)'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    volume = models.CharField(max_length=20)
    abv = models.CharField(max_length=10, choices=ABV_CHOICES)
    emoji = models.CharField(max_length=8)
    tags = models.JSONField(default=list)

    def __str__(self):
        return self.name
