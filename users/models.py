from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.urls import reverse

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'admin'),
        (2, 'professeur'),
        (3, 'étudiant'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, default='profile_pictures/1_e3DaScz.jpg')

    # ===== دليل قانوني 09-08 =====
    accepted_reglement_at = models.DateTimeField(null=True, blank=True, verbose_name="Date acceptation règlement")
    ip_at_registration = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    last_seen = models.DateTimeField(default=timezone.now)

    # ===== الموافقة القانونية =====
    accepted_reglement = models.BooleanField(default=False, verbose_name="A accepté le règlement")
    accepted_0908 = models.BooleanField(default=False, verbose_name="A accepté la Loi 09-08")
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

class Friendship(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friendship_requests_received', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ===== شهادة لكل publication - كتحمل الأستاذ المسؤولية =====
    is_original = models.BooleanField(default=False, verbose_name="Certifié œuvre originale")
    has_consent_0908 = models.BooleanField(default=False, verbose_name="Respect Loi 09-08 certifié")
    contains_personal_data = models.BooleanField(default=False, verbose_name="Contient données perso (nécessite preuve)")
    consent_proof = models.FileField(upload_to='consents_0908/', null=True, blank=True, verbose_name="Preuve consentement écrit")

    def __str__(self):
        return f"Post {self.id} by {self.user}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    NOTIF_TYPES = (
        ('general', 'General'),
        ('payment', 'Paiement'),
        ('student', 'Etudiant'),
        ('course', 'Cours'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('friend', 'Amitié'),
        ('message', 'Message'),
        ('legal_0908', 'Signalement 09-08'), # جديد
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES, default='general')
    related_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.message}"

    def get_absolute_url(self):
        if self.link:
            return self.link
        return reverse('home')