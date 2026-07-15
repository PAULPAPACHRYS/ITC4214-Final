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

    # Catch-all: anything that matched none of the addresses above lands here.
    # It MUST stay last, because Django tries these patterns in order - put any
    # higher up and it would swallow the real pages below it.
    #
    # This is what catches an address typed by hand into the browser bar. It is
    # here as well as handler404 below because handler404 is only used when
    # DEBUG is False; with DEBUG on, Django shows its own yellow debug page
    # instead. The catch-all works either way, so the friendly page is shown in
    # development and in production alike.
    re_path(r'^.*$', page_views.not_found),
]

# Used by Django whenever a view raises Http404 (for example an unknown table on
# the Database page, or a product id that does not exist). This one only takes
# effect when DEBUG = False.
handler404 = 'pages.views.not_found'
