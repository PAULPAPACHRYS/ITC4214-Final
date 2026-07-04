from django.contrib import admin
from .models import Brand, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subcategory')
    list_filter = ('name',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'price', 'volume', 'abv')
    list_filter = ('category__name', 'brand')
    search_fields = ('name',)
