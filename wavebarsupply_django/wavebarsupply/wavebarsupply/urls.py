from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('browse/', include('catalogue.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    path('database/', include('database.urls')),
]
