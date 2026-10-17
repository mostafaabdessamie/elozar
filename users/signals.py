from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, Profile, Friendship, Comment, Notification

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=Friendship)
def create_friend_request_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.to_user,
            message=f"{instance.from_user.username} vous a envoyé une demande d'ami.",
            link=f"/profile/{instance.from_user.id}/",
            notif_type='friend',
            related_id=instance.id
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        if instance.post.user == instance.user:
            return
        Notification.objects.create(
            user=instance.post.user,
            message=f"{instance.user.username} علّق على تدوينتك.",
            content=instance.content[:100],
            link=f"/chat/post/{instance.post.id}/",  
            notif_type='comment',
            related_id=instance.post.id
        )