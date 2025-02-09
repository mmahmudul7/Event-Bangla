from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from events.models import Event, UserProfile

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"

        subject = 'Activate Your Account'
        message = f'Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_url}\n\nThank You!'
        recipient_list = [instance.email]

        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            print(f"Failed to send email to {instance.email}: {str(e)}")


@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name='User')
        instance.groups.add(user_group)
        instance.save()


@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_confirmation(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            user = instance.participants.get(id=user_id)
            send_mail(
                subject="RSVP Confirmation",
                message=f"Hello {user.username},\n\nYou have successfully RSVP'd for the event '{instance.name}'.",
                from_email="noreply@eventbangla.com",
                recipient_list=[user.email],
                fail_silently=True,
            )



# @receiver(post_save, sender=User)
# def assign_role(sender, instance, created, **kwargs):
#     if created:
#         user_group, created = Group.objects.get_or_create(name='User')
#         instance.groups.add(user_group)
#         instance.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """New user become participant always"""
    if created:
        UserProfile.objects.create(user=instance, role='participant')


@receiver(post_save, sender=Event)
def update_user_role(sender, instance, created, **kwargs):
    """participant to 'organizer' """
    if created:
        user_profile, _ = UserProfile.objects.get_or_create(user=instance.organizer)
        if user_profile.role == 'participant':  # if participant then update
            user_profile.role = 'organizer'
            user_profile.save()
