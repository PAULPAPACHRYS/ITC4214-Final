from django.contrib import admin
from .models import Preset


@admin.register(Preset)
class PresetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'color')
    list_filter = ('user',)
    search_fields = ('name',)
    filter_horizontal = ('ingredients',)
