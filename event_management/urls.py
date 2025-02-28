from django.contrib import admin
from django.urls import path, include
from core.views import no_permission
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('users/', include('users.urls')),
    path('no-permission/', no_permission, name='no-permission')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)