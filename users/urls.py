from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, assign_role, redirect_dashboard

urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='sign-out'),

    path('users/activate/<int:user_id>/<str:token>/', activate_user, name='activate'),

    # path('events/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),

    path('admin/assign-role/<int:user_id>/', assign_role, name='assign-role'),
    path('dashboard/', redirect_dashboard, name='dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
]