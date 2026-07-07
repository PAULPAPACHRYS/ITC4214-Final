from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view'),
    path('add/', views.add, name='add'),
    path('update/', views.update, name='update'),
    path('remove/', views.remove, name='remove'),
]
