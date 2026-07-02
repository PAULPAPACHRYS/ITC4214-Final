from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Extra trade-account details that don't fit on the built-in User model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bar_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.bar_name} ({self.user.username})"
