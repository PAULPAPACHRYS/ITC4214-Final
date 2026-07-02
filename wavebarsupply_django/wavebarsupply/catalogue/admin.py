from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'subcategory', 'price')
    list_filter = ('category', 'subcategory', 'abv')
    search_fields = ('name', 'brand')
