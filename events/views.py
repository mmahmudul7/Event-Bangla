from django.shortcuts import render, redirect, get_object_or_404
from events.forms import EventForm, CategoryForm
from events.models import Event, Category
from django.utils.timezone import now
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.views import is_admin
from datetime import date
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


User = get_user_model()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer_or_admin(user):
    return is_organizer(user) or is_admin(user)

# Event List view
def event_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category')
    query = request.GET.get('q', '')

    # events = Event.objects.select_related('category').all()
    events = Event.objects.select_related('category').prefetch_related('participants').all()


    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])
    if category_id:
        events = events.filter(category_id=category_id)
    if query:
        events = events.filter(Q(name__icontains=query) | Q(location__icontains=query))

    # events = events.prefetch_related('participants')
    categories = Category.objects.all()
    total_participants = User.objects.filter(rsvp_events__isnull=False).distinct().count()


    context = {
        'events': events,
        'categories': categories,
        'total_participants': total_participants,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, id):
    # event = get_object_or_404(Event, id=id)
    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('participants'), id=id)

    return render(request, 'events/event_detail.html', {'event': event})


# Admin and Organizer Decorator
admin_and_organizer_decorators = [
    login_required,
    user_passes_test(is_organizer_or_admin, login_url='no-permission')
]

# Event Create Views
@method_decorator(admin_and_organizer_decorators, name='dispatch')
class EventCreate(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def get_success_url(self):
        return self.request.GET.get('next', 'dashboard')

    def form_valid(self, form):
        event = form.save(commit=False)
        event.organizer = self.request.user
        event.save()
        form.save_m2m()
        messages.success(self.request, 'Event created successfully!')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = self.get_success_url()
        return context


# Event Update View
@method_decorator(admin_and_organizer_decorators, name='dispatch')
class EventUpdate(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if request.user != event.organizer and not request.user.is_superuser:
            messages.error(request, "You are not authorized to edit this event.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Event updated successfully!')
        return redirect(reverse('event_detail', kwargs={'id': self.object.id}))


# Event Delete View
class EventDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        event = get_object_or_404(Event, id=self.kwargs['pk'])
        return self.request.user == event.organizer or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You are not authorized to delete this event.")
        return redirect('dashboard')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Event deleted successfully!")
        return super().delete(request, *args, **kwargs)


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Name: {name}, Email: {email}, Message: {message}")
    return render(request, 'events/contact.html')


@login_required
@user_passes_test(is_participant, login_url='no-permission')
def event_rsvp(request, id):
    event = get_object_or_404(Event, id=id)
    user = request.user

    if user in event.participants.all():
        event.participants.remove(user)
        messages.success(request, 'You have successfully canceled your RSVP.')
    else:
        event.participants.add(user)
        messages.success(request, 'You have successfully RSVP for the event.')

    return redirect(reverse('event_detail', kwargs={'id': event.id}))


@login_required
def participant_list(request):
    participants = User.objects.filter(rsvp_events__isnull=False).distinct().order_by('username')  
    return render(request, 'events/participant_list.html', {'participants': participants})


# Oranizer Dashboard View
class OrganizerDashboard(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Event
    template_name = "events/organizer_dashboard.html"
    context_object_name = "events"

    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, 'userprofile', None) and self.request.user.userprofile.role == "organizer"

    def get_queryset(self):
        today = timezone.now().date()
        events = Event.objects.select_related("category").prefetch_related("participants").all()
        filtered_events = events.filter(date=today)
        filter_title = "Today's Events"

        # Apply filters
        filter = self.request.GET.get("filter")
        category = self.request.GET.get("category")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if filter == "upcoming_events":
            filtered_events = events.filter(date__gte=timezone.now())
            filter_title = "Upcoming Events"
        elif filter == "past_events":
            filtered_events = events.filter(date__lt=timezone.now())
            filter_title = "Past Events"
        elif filter == "total_events":
            filtered_events = events
            filter_title = "All Events"

        if category:
            filtered_events = events.filter(category__name=category)
            filter_title = f"Events in {category} Category"

        if start_date and end_date:
            filtered_events = events.filter(date__range=[start_date, end_date])
            filter_title = f"Events from {start_date} to {end_date}"

        self.filter_title = filter_title
        return filtered_events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        context["total_participants"] = User.objects.filter(rsvp_events__isnull=False).distinct().count()
        context["total_events"] = Event.objects.count()
        context["total_upcoming_events"] = Event.objects.filter(date__gte=timezone.now()).count()
        context["total_past_events"] = Event.objects.filter(date__lt=timezone.now()).count()
        context["filtered_events"] = self.get_queryset()
        context["categories"] = Category.objects.all()
        context["filter_title"] = self.filter_title
        context["today_events"] = Event.objects.filter(date=today)
        context["myEvents"] = Event.objects.filter(organizer=self.request.user)

        return context


# Paticipant dashbaord 
@login_required
@user_passes_test(is_participant, login_url='no-permission')
def participant_dashboard(request):
    today = timezone.now().date()

    events = Event.objects.select_related('category').prefetch_related('participants').all()
    today_events = events.filter(date=today)
    # today_events = Event.objects.filter(date=today)
    rsvp_events = request.user.rsvp_events.all()

    total_participants = Event.objects.aggregate(total=Count('participants', distinct=True))['total'] or 0
    total_events = Event.objects.count()
    total_upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_past_events = Event.objects.filter(date__lt=timezone.now()).count()

    # events = Event.objects.select_related('category').all()
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
        'rsvp_events': rsvp_events
    }
    
    return render(request, 'events/participant_dashboard.html', context)


# Create Category View 
class CategoryCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("dashboard")

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Organizer").exists()

    def form_valid(self, form):
        category = form.save(commit=False)
        if self.request.user.groups.filter(name="Organizer").exists():
            category.organizer = self.request.user
        category.save()
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "You are not authorized to create a category.")
        return redirect("dashboard")


@login_required
@user_passes_test(is_organizer_or_admin, login_url='no-permission')
def category_update(request, id):
    category = get_object_or_404(Category, id=id)

    # if category.organizer is None or (request.user != category.organizer and not request.user.is_superuser):
    if category.organizer != request.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to edit this category.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("dashboard")
    else:
        form = CategoryForm(instance=category)

    return render(request, "events/category_form.html", {"form": form})



@login_required
@user_passes_test(is_organizer_or_admin, login_url='no-permission')
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)

    if request.user == category.organizer or request.user.is_superuser:
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('dashboard')
    else:
        messages.error(request, 'You are not authorized to delete this category.')
        return redirect('dashboard')
