from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from users.forms import CustomRegistrationForm, AssignRoleForm, CreateGroupForm
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from events.models import Event, Category, UserProfile
from datetime import date
from django.utils import timezone
from django.db.models import Count, Prefetch

# Create your views here.
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
        else:
            print("Form is not valid")
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
def admin_dashboard(request):
    today = date.today()
    today_events = Event.objects.filter(date=today)

    total_participants = Event.objects.aggregate(total=Count('participants', distinct=True))['total'] or 0
    total_events = Event.objects.count()
    total_upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_past_events = Event.objects.filter(date__lt=timezone.now()).count()

    events = Event.objects.select_related('category').all()
    filter = request.GET.get('filter', None)
    category = request.GET.get('category', None)
    filter_title = "Today's Events"
    filtered_events = []

    if not filter:
        today = timezone.now().date()
        filtered_events = events.filter(date=today)
        filter_title = "Today's Events"

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
        'today_events': today_events,
    }
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    print(users)

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = 'No Group Assigned'

    return render(request, 'admin/admin_dashboard.html', {"users": users}, context)



@login_required
def redirect_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.role == "admin":
        return redirect("admin-dashboard")
    elif user_profile.role == "organizer":
        return redirect("organizer-dashboard")
    elif user_profile.role == "participant":
        return redirect("participant-dashboard")
    else:
        return redirect('no-permission')
    

def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')

    return render(request, 'admin/create_group.html', {'form': form})



def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
    if form.is_valid():
        role = form.cleaned_data.get('role')
        user.groups.clear() # Remove old roles
        user.groups.add(role)
        messages.success(request, f"User {user.username} has been assigned to the {role.name} role")
        return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form})



def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups})


