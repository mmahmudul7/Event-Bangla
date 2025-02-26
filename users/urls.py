from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, redirect_dashboard, create_group, assign_role, group_list, user_list, remove_participant, ProfileView

urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='sign-out'),
    path('activate/<int:user_id>/<str:token>/', activate_user, name='activate'),
    path('dashboard/', redirect_dashboard, name='dashboard'),
    path('admin/admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/assign-role/<int:user_id>/', assign_role, name='assign-role'),
    path('admin/group-list', group_list, name='group-list'),
    path('admin/user-list', user_list, name='user-list'),
    path('admin/remove/<int:user_id>/', remove_participant, name='remove-participant'),
    path('profile/', ProfileView.as_view(), name='profile'),
]