from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, pre_save
from django.contrib.auth.models import User
from .models import Notification, Profile
import os
from django.conf import settings


# for creating a profile for a new user and sending notification

# signal that gets fired after the user is saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        new_profile = Profile(user=instance)
        new_profile.save()
        notification = Notification(
            user_notify=instance, notify_reason='welcome')
        notification.save()


"""
@receiver(post_save,sender=User)
def save_user_profile(sender,instance,**kwargs):
    Profile.save()
"""

# for deleting the cover and profile picture before deleting profile


@receiver(pre_delete, sender=Profile)
def delete_pictures_on_profile_delete(sender, instance, **kwargs):
    if instance.profile_pic.url != '/media/profile_pic/default.jpg':
        # instance.profile_pic.delete()
        os.remove(os.path.join(settings.MEDIA_ROOT,
                               'profile_pic', instance.profile_pic.url[19:]))
    if instance.cover_pic.url != '/media/cover_pic/default.jpg':
        # instance.cover_pic.delete()
        os.remove(os.path.join(settings.MEDIA_ROOT,
                               'cover_pic', instance.cover_pic.url[17:]))
