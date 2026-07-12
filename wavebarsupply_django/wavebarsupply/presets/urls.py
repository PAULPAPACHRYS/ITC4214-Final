from django.urls import path
from . import views

app_name = 'presets'

urlpatterns = [
    path('create/', views.create, name='create'),
    path('<int:preset_id>/edit/', views.edit, name='edit'),
    path('<int:preset_id>/delete/', views.delete, name='delete'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]
