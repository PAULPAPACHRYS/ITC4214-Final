from django.urls import path
from . import views

app_name = 'likes'

urlpatterns = [
    path('toggle/', views.toggle, name='toggle'),
]
