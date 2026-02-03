"""
URL configuration for allminnesota_project.
Includes Django admin and core app URLs. Serves media in DEBUG.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personalize Django admin for All Minnesota
admin.site.site_header = 'All Minnesota Administration'
admin.site.site_title = 'All Minnesota Admin'
admin.site.index_title = 'Site administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
