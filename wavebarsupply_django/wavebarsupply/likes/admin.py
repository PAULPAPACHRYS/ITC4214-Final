from django.contrib import admin
from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user')
    search_fields = ('product__name', 'user__email')
