from django.contrib import admin
from .models import Brand, Category, Product, Subcategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'image')
    list_filter = ('category',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'subcategory', 'price', 'volume', 'abv')
    list_filter = ('subcategory__category', 'brand')
    search_fields = ('name',)
