from django.conf import settings
from django.db import models


class Preset(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#2A9D8F')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='presets')
    ingredients = models.ManyToManyField('catalogue.Product', related_name='presets')

    class Meta:
        db_table = 'presets'

    def __str__(self):
        return f"{self.name} ({self.user.email if self.user else 'default'})"

    def to_dict(self):
        ingredients = list(self.ingredients.all())
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'ingredient_ids': [p.id for p in ingredients],
            'ingredient_names': [p.name for p in ingredients],
        }
