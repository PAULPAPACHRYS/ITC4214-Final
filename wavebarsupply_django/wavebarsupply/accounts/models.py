from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models

from .validators import clean_email, clean_text, name_validator, phone_validator


class UsersManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email address is required.')
        email = clean_email(self.normalize_email(email))
        user = self.model(email=email, **extra_fields)
        user.set_password(password)          # hashed with bcrypt (in settings.py under PASSWORD_HASHERS)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]

    first_name = models.CharField(max_length=50, validators=[name_validator])
    last_name = models.CharField(max_length=50, validators=[name_validator])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    bar_name = models.CharField(max_length=100, blank=True, default='')
    bar_location = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True, default='',
                             validators=[phone_validator])

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        self.email = clean_email(self.email)
        self.first_name = clean_text(self.first_name)
        self.last_name = clean_text(self.last_name)
        self.bar_name = clean_text(self.bar_name)
        return super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
