from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=17, unique=True, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images', blank=True, default='profile_images/default.png')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username