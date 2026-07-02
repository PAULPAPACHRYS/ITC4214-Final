from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bar_name', 'location', 'phone')
    search_fields = ('bar_name', 'user__username')
