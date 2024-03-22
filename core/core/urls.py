from django.contrib import admin
from django.urls import path, include
from django.views.defaults import page_not_found as default_page_not_found

handler404 = default_page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('analyze/', include('scraper.urls')),
    path('reports/', include('reports.urls')),
    path('articles/', include('articles.urls')),
]
