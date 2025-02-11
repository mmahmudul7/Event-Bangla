from django.contrib import admin
from django.urls import path, include
from core.views import no_permission

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('users/', include('users.urls')),
    path('no-permission/', no_permission, name='no-permission')
]
