from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm
from django.contrib import messages
from users.forms import LoginForm, CustomRegistrationForm, AssignRoleForm, CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm, EditProfileForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from events.models import Event, Category, UserProfile
from datetime import date
from django.utils import timezone
from django.db.models import Count, Prefetch
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model


User = get_user_model()

# Edit User Profile
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        form.save()
        return redirect('profile')

# Create your views here.
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def sign_up(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()

            participant_group = Group.objects.get(name='Participant')
            user.groups.add(participant_group)

            UserProfile.objects.create(user=user)

            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
        else:
            print("Form is not valid")
    else:
        form = CustomRegistrationForm()

    return render(request, 'registration/register.html', {"form": form})

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    return render(request, 'registration/login.html', {'form': form})


@login_required
def sign_out(request):
    # if request.method == 'POST':
    logout(request)
    return redirect('sign-in')


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')
    

# Admin dashboard 
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    events = Event.objects.select_related('category').prefetch_related('participants').all()

    total_participants = Event.objects.aggregate(total=Count('participants', distinct=True))['total'] or 0
    # total_events = Event.objects.count()
    total_events = len(events)
    total_upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_past_events = Event.objects.filter(date__lt=timezone.now()).count()

    filter = request.GET.get('filter', None)
    category = request.GET.get('category', None)
    # filter_title = "Today's Events"
    # filtered_events = []
    filtered_events = events 

    if not filter:
        # filtered_events = events.filter(date=today)
        filter_title = "All Events"

    if filter == 'upcoming_events':
        filtered_events = events.filter(date__gte=timezone.now())
        filter_title = "Upcoming Events"
    elif filter == 'past_events':
        filtered_events = events.filter(date__lt=timezone.now())
        filter_title = "Past Events"
    elif filter == 'total_events':
        filtered_events = events
        filter_title = "All Events"
    
    if category:
        filtered_events = events.filter(category__name=category)
        filter_title = f"Events in {category} Category"

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        filtered_events = events.filter(date__range=[start_date, end_date])
        filter_title = f"Events from {start_date} to {end_date}"

    categories = Category.objects.all()

    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'

    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'total_upcoming_events': total_upcoming_events,
        'total_past_events': total_past_events,
        'events': events,
        'filtered_events': filtered_events,
        'categories': categories,
        'start_date': start_date,
        'end_date': end_date,
        'filter_title': filter_title,
        # 'today_events': today_events,
        "users": users,
    }

    return render(request, 'admin/admin_dashboard.html', context)



@login_required
def redirect_dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.user.is_superuser:
        return redirect('admin-dashboard')
    elif request.user.groups.filter(name='Organizer').exists():
        return redirect('organizer-dashboard')
    elif request.user.groups.filter(name='Participant').exists():
        return redirect('participant-dashboard')
    else:
        return redirect('no-permission')


@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')

    return render(request, 'admin/create_group.html', {'form': form})


@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
    if form.is_valid():
        role = form.cleaned_data.get('role')
        user.groups.clear()
        user.groups.add(role)
        messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
        return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form})


@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups})


@user_passes_test(is_admin, login_url='no-permission')
@login_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/user_list.html', {'users': users})


@user_passes_test(is_admin, login_url='no-permission')
def remove_participant(request, user_id):
    user = get_object_or_404(User, id=user_id)
    participant_group = Group.objects.filter(name="Participant").first()

    if participant_group and participant_group in user.groups.all():
        user.groups.remove(participant_group)
        user.rsvp_events.clear()
        messages.success(request, f"{user.username} removed from Participants.")
    else:
        messages.error(request, "User is not a participant.")

    return redirect('user-list')


# Profile View
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['phone'] = user.phone
        context['bio'] = user.bio
        context['profile_image'] = user.profile_image

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login

        return context


# Change Password view
class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm


# Custom Change Password Reset View
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        context['profile_image'] = self.request.user.profile_image
        # print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset eamil sent. Please check your email'
        )
        return super().form_valid(form)


# Custom Password Reset Confirm View
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully'
        )
        return super().form_valid(form)
