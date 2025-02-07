from django.urls import path
from events import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.event_list, name='event_list'),  # Event list page
    path('events/<int:id>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:id>/update/', views.event_update, name='event_update'),
    path('events/<int:id>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:id>/rsvp/', views.event_rsvp, name='event_rsvp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('participants/', views.participant_list, name='participant_list'),
    path('contact/', views.contact_page, name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
