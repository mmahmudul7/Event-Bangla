from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, redirect_dashboard, create_group, assign_role, group_list, user_list, remove_participant, ProfileView, EditProfileView, CustomPasswordResetView, CustomPasswordResetConfirmView, ChangePassword
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView


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
    path('edit-profile', EditProfileView.as_view(), name='edit_profile'),
    path('password-reset', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-change/', ChangePassword.as_view(), name='password_change'),
    path('password-change/done', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
]