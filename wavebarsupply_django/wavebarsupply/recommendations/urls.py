from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('cart/', views.for_cart, name='cart'),
]
