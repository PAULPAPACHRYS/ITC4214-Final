from django.urls import path
from . import views

app_name = 'database'

urlpatterns = [
    path('', views.home, name='home'),
    path('<str:key>/add/', views.add, name='add'),
    path('<str:key>/<int:pk>/edit/', views.edit, name='edit'),
    path('<str:key>/<int:pk>/delete/', views.delete, name='delete'),
    path('<str:key>/', views.table, name='table'),
]
