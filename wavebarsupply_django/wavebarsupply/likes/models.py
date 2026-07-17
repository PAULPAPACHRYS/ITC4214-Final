from django.conf import settings
from django.db import models


class Like(models.Model):
    product = models.ForeignKey(
        'catalogue.Product', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'likes'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'], name='unique_like_per_user_product'),
        ]

    def __str__(self):
        return f"{self.user} likes {self.product}"
