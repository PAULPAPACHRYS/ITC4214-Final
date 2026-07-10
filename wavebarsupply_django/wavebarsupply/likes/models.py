from django.conf import settings
from django.db import models


class Like(models.Model):
    """A single "like" of a product by a user.

    Columns: id (pk), product_id (fk), user_id (fk).

    Each row is one user liking one product. The count of likes for a product is
    simply how many rows point at it, so the rows are the single source of truth
    (no separate counter to keep in sync). The unique constraint below stops a
    user from liking the same product twice.
    """
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
