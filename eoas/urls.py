"""
URL configuration for eoas project.
Sistem Manajemen Operasional & Absensi Educourse (EOAS).
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('scheduling/', include('scheduling.urls')),
    path('attendance/', include('attendance.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('dashboard.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
