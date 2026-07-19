from django.contrib import admin
from django.urls import path, include, re_path

from pages import views as page_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('browse/', include('catalogue.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('pages.urls')),
    path('database/', include('database.urls')),
    path('cart/', include('cart.urls')),
    path('likes/', include('likes.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('presets/', include('presets.urls')),

        
    #Catch-all: anything that matched none of the addresses above lands here
    #it must stay last because Django tries these patterns in order
    
    #this is what catches an address typed by hand into the browser bar
    #handler404 below is only used when DEBUG is False;
    #with DEBUG = True, Django shows its own yellow debug page instead

    #with this line and the handler404 it works either way, 
    #so the friendly page is shown in development and in production alike
    re_path(r'^.*$', page_views.not_found),
]

"""
used by Django whenever a view raises Http404 
for example an unknown table on the Database page, or a product id that does not exist
this one only takes effect when DEBUG = False
"""
handler404 = 'pages.views.not_found'
