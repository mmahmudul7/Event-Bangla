from django.urls import path
from events import views
from django.conf import settings
from django.conf.urls.static import static
from events.views import event_list, event_detail, event_create, event_update, event_delete, event_rsvp, participant_list, contact_page, organizer_dashboard, participant_dashboard


urlpatterns = [
    path('', event_list, name='event_list'),  # Event list page
    path('events/<int:id>/', event_detail, name='event_detail'),
    path('events/create/', event_create, name='event_create'),
    path('events/<int:id>/update/', event_update, name='event_update'),
    path('events/<int:id>/delete/', event_delete, name='event_delete'),
    path('events/<int:id>/rsvp/', event_rsvp, name='event_rsvp'),
    path('participants/', participant_list, name='participant_list'),
    path('contact/', contact_page, name='contact'),
    path('organizer-dashboard/', organizer_dashboard, name='organizer-dashboard'),
    path('participant-dashboard/', participant_dashboard, name='participant-dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
