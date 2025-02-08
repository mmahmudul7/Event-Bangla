from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='events', on_delete=models.CASCADE)
    event_image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    participants = models.ManyToManyField(User, related_name='rsvp_events', blank=True)

    def __str__(self):
        return self.name

    def add_rsvp(self, user):
        """A user cannot RSVP twice."""
        if not self.participants.filter(id=user.id).exists():
            self.participants.add(user)
            return True
        return False
