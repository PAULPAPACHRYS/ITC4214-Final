from django.conf import settings
from django.db import models


class Preset(models.Model):
    """A cocktail preset: a named, coloured bundle of ingredient products.

    - user is null for the built-in default presets everyone sees; a non-null
      user means a preset only that user created and can see.
    - ingredients is the set of products the cocktail needs. Adding a preset to
      the cart adds every ingredient, each with quantity = the servings chosen.
    """
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#2A9D8F')   # hex, e.g. #2A9D8F
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='presets')
    ingredients = models.ManyToManyField('catalogue.Product', related_name='presets')

    class Meta:
        db_table = 'presets'

    def __str__(self):
        return f"{self.name} ({self.user.email if self.user else 'default'})"

    def to_dict(self):
        """Shape used by the front-end to build a preset card."""
        ingredients = list(self.ingredients.all())
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'ingredient_ids': [p.id for p in ingredients],
            'ingredient_names': [p.name for p in ingredients],
        }
