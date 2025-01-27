from django.shortcuts import render, redirect, get_object_or_404
from events.forms import EventForm
from events.models import Event, Participant, Category
from django.utils.timezone import now
from django.db.models import Q, Count
from datetime import date
from django.utils import timezone
from django.contrib import messages

# Event List view
def event_list(request):
    # Get the filter values from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category')
    query = request.GET.get('q', '')

    # Start with all events and apply select_related for category optimization
    events = Event.objects.select_related('category').all()

    # Apply date range filter if both dates are provided
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])

    # Apply category filter if category_id is provided
    if category_id:
        events = events.filter(category_id=category_id)

    # Apply search filter if query is provided
    if query:
        events = events.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    # Use prefetch_related for fetching participants in bulk for optimization
    events = events.prefetch_related('participants')

    # Fetch categories for the filter dropdown
    categories = Category.objects.all()

    # Aggregate query to calculate the total number of participants across all events
    total_participants = Participant.objects.aggregate(total_participants=Count('id'))['total_participants']

    # Pass filtered events and categories to the template
    context = {
        'events': events,
        'categories': categories,
        'total_participants': total_participants,
    }

    return render(request, 'events/event_list.html', context)

# Event Detail view
def event_detail(request, id):
    event = Event.objects.get(id=id)
    return render(request, 'events/event_detail.html', {'event': event})

# Event Create view
def event_create(request):
    next_url = request.GET.get('next', 'dashboard')
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Previous entry added successfully!')
            return redirect(next_url)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'next_url': next_url})

# Event Update view
def event_update(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

# Event Delete view
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('dashboard')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

# Dashboard 
def dashboard(request):
    # Stats
    today = date.today()
    today_events = Event.objects.filter(date=today)

    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    total_upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_past_events = Event.objects.filter(date__lt=timezone.now()).count()

    # Filter and Events
    events = Event.objects.select_related('category').all()  # Optimize with select_related
    filter = request.GET.get('filter', None)
    category = request.GET.get('category', None)
    filter_title = "Today's Events"  # Default title
    filtered_events = []

    # Default to today's events
    if not filter:
        today = timezone.now().date()
        filtered_events = events.filter(date=today)
        filter_title = "Today's Events"

    # Card Filter Logic
    if filter == 'upcoming_events':
        filtered_events = events.filter(date__gte=timezone.now())
        filter_title = "Upcoming Events"
    elif filter == 'past_events':
        filtered_events = events.filter(date__lt=timezone.now())
        filter_title = "Past Events"
    elif filter == 'total_events':
        filtered_events = events
        filter_title = "All Events"

    # Category Filter Logic
    if category:
        filtered_events = events.filter(category__name=category)
        filter_title = f"Events in {category} Category"

    # Date Filter Logic (from the date input fields)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        filtered_events = events.filter(date__range=[start_date, end_date])
        filter_title = f"Events from {start_date} to {end_date}"

    # Categories
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
        'categories': Category.objects.all(),
    }

    return render(request, 'events/dashboard.html', context)

# Contact 
def contact_page(request):
    if request.method == "POST":
        # Handle the form submission logic here (e.g., send email, save to database)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Add logic for handling the submitted data
        print(f"Name: {name}, Email: {email}, Message: {message}")
    return render(request, 'events/contact.html')

# Participant List 
def participant_list(request):
    participants = Participant.objects.all()
    context = {
        'participants': participants,
    }
    return render(request, 'events/participant_list.html', context)















# from django.shortcuts import render, redirect, get_object_or_404
# from events.forms import EventForm, ParticipantForm, CategoryForm
# from events.models import Event, Participant, Category
# from django.utils.timezone import now
# from django.db.models import Q
# from datetime import date, timedelta
# from django.utils import timezone
# from django.utils.dateparse import parse_date
# from django.contrib import messages

# # Event List view

# def event_list(request):
#     # Get the filter values from GET request
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     category_id = request.GET.get('category')
#     query = request.GET.get('q', '')

#     # Start with all events
#     events = Event.objects.all()

#     # Apply date range filter if both dates are provided
#     if start_date and end_date:
#         events = events.filter(date__range=[start_date, end_date])

#     # Apply category filter if category_id is provided
#     if category_id:
#         events = events.filter(category_id=category_id)

#     # Apply search filter if query is provided
#     if query:
#         events = events.filter(
#             name__icontains=query
#         ) | events.filter(
#             location__icontains=query
#         )

#     # Fetch categories for the filter dropdown
#     categories = Category.objects.all()

#     # Pass filtered events and categories to the template
#     context = {
#         'events': events,
#         'categories': categories,
#     }

#     return render(request, 'events/event_list.html', context)


# # Event Detail view
# def event_detail(request, id):
#     event = Event.objects.get(id=id)
#     return render(request, 'events/event_detail.html', {'event': event})

# # Event Create view
# from django.shortcuts import render, redirect, get_object_or_404
# from .forms import EventForm
# from .models import Event

# def event_create(request):
#     next_url = request.GET.get('next', 'dashboard')
#     if request.method == "POST":
#         form = EventForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect(next_url)
#     else:
#         form = EventForm()
#     return render(request, 'events/event_form.html', {'form': form, 'next_url': next_url})

# # def event_create(request):
# #     if request.method == 'POST':
# #         form = EventForm(request.POST, request.FILES)
# #         if form.is_valid():
# #             form.save()
# #             return redirect('event_list')
# #     else:
# #         form = EventForm()
# #     return render(request, 'events/event_form.html', {'form': form})

# # Event Update view
# def event_update(request, id):
#     event = get_object_or_404(Event, id=id)
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES, instance=event)
#         if form.is_valid():
#             form.save()
#             return redirect('event_detail', id=event.id)
#     else:
#         form = EventForm(instance=event)
#     return render(request, 'events/event_form.html', {'form': form})

# # Event Delete view
# def event_delete(request, id):
#     event = get_object_or_404(Event, id=id)
#     if request.method == 'POST':
#         event.delete()
#         messages.success(request, 'Event deleted successfully!')
#         return redirect('dashboard')
#     return render(request, 'events/event_confirm_delete.html', {'event': event})

# # Dashboard 
# def dashboard(request):
#     # Stats
#     today = date.today()
#     today_events = Event.objects.filter(date=today)

#     total_participants = Participant.objects.count()
#     total_events = Event.objects.count()
#     total_upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
#     total_past_events = Event.objects.filter(date__lt=timezone.now()).count()

#     # Filter and Events
#     events = Event.objects.all()
#     filter = request.GET.get('filter', None)
#     category = request.GET.get('category', None)
#     filter_title = "Today's Events"  # Default title
#     filtered_events = []

#     # Default to today's events
#     if not filter:
#         today = timezone.now().date()
#         filtered_events = events.filter(date=today)
#         filter_title = "Today's Events"

#     # Card Filter Logic
#     if filter == 'upcoming_events':
#         filtered_events = events.filter(date__gte=timezone.now())
#         filter_title = "Upcoming Events"
#     elif filter == 'past_events':
#         filtered_events = events.filter(date__lt=timezone.now())
#         filter_title = "Past Events"
#     elif filter == 'total_events':
#         filtered_events = events
#         filter_title = "All Events"

#     # Category Filter Logic
#     if category:
#         filtered_events = events.filter(category__name=category)
#         filter_title = f"Events in {category} Category"

#     # Date Filter Logic (from the date input fields)
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#     if start_date and end_date:
#         filtered_events = events.filter(date__range=[start_date, end_date])
#         filter_title = f"Events from {start_date} to {end_date}"

#     # Categories
#     categories = Category.objects.all()

#     context = {
#         'total_participants': total_participants,
#         'total_events': total_events,
#         'total_upcoming_events': total_upcoming_events,
#         'total_past_events': total_past_events,
#         'events': events,
#         'filtered_events': filtered_events,
#         'categories': categories,
#         'start_date': start_date,
#         'end_date': end_date,
#         'filter_title': filter_title,

#         'today_events': today_events,
#         'categories': Category.objects.all(),
#     }

#     return render(request, 'events/dashboard.html', context)




# # Contact 

# def contact_page(request):
#     if request.method == "POST":
#         # Handle the form submission logic here (e.g., send email, save to database)
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         message = request.POST.get('message')
#         # Add logic for handling the submitted data
#         print(f"Name: {name}, Email: {email}, Message: {message}")
#     return render(request, 'events/contact.html')


# # Paticipant List 
# def participant_list(request):
#     participants = Participant.objects.all()
#     context = {
#         'participants': participants,
#     }
#     return render(request, 'events/participant_list.html', context)
