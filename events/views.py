from django.shortcuts import render, redirect, get_object_or_404
from events.forms import EventForm
from events.models import Event, Category
from django.utils.timezone import now
from django.db.models import Q, Count
from datetime import date
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Event List view
# @login_required
def event_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category')
    query = request.GET.get('q', '')

    events = Event.objects.select_related('category').all()

    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])
    if category_id:
        events = events.filter(category_id=category_id)
    if query:
        events = events.filter(Q(name__icontains=query) | Q(location__icontains=query))

    events = events.prefetch_related('participants')
    categories = Category.objects.all()
    total_participants = Event.objects.aggregate(total=Count('participants', distinct=True))['total'] or 0

    context = {
        'events': events,
        'categories': categories,
        'total_participants': total_participants,
    }
    return render(request, 'events/event_list.html', context)

@login_required
def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required
def event_create(request):
    next_url = request.GET.get('next', 'dashboard')
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            form.save_m2m()
            messages.success(request, 'Event created successfully!')
            return redirect(next_url)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'next_url': next_url})

@login_required
def event_update(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user != event.organizer:
        messages.error(request, "You are not authorized to edit this event.")
        return redirect('event_list')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

@login_required
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user != event.organizer:
        messages.error(request, "You are not authorized to delete this event.")
        return redirect('event_list')
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('dashboard')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
def dashboard(request):
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
    return render(request, 'events/dashboard.html', context)

# @login_required
def contact_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Name: {name}, Email: {email}, Message: {message}")
    return render(request, 'events/contact.html')


@login_required
def event_rsvp(request, id):
    event = get_object_or_404(Event, id=id)
    user = request.user
    if user in event.participants.all():
        event.participants.remove(user)
        messages.success(request, 'You have successfully canceled your RSVP.')
    else:
        event.participants.add(user)
        messages.success(request, 'You have successfully RSVP’d for the event.')
    return redirect('event_detail', id=event.id)


@login_required
def participant_list(request):
    participants = User.objects.filter(rsvp_events__isnull=False).distinct().order_by('username')  
    return render(request, 'events/participant_list.html', {'participants': participants})
