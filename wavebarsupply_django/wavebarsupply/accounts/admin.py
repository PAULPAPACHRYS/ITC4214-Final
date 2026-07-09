from django.contrib import admin
from .models import Users


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'role', 'bar_name', 'bar_location', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email', 'bar_name')
    readonly_fields = ('password', 'last_login')
