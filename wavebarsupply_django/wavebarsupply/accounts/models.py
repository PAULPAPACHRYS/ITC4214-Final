from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models


class UsersManager(BaseUserManager):
    """Manager required by Django for a custom auth user model."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email address is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)          # hashed with bcrypt (see PASSWORD_HASHERS)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    """Site accounts, and also Django's authentication user model.

    Being the auth user model is what lets the built-in UserCreationForm and
    AuthenticationForm work. The password is stored hashed (bcrypt) by Django's
    password hashers; login is by email.
    """

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]

    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    bar_name = models.CharField(max_length=100, blank=True, default='')
    bar_location = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')

    # Flags Django's auth/admin need.
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'users'

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def __str__(self):
        return f"{self.full_name} ({self.email})"
