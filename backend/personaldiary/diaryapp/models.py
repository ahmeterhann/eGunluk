from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Diary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diaries')
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.date})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)  # Hakkında
    gender = models.CharField(max_length=10, choices=[('Erkek', 'Erkek'), ('Kadın', 'Kadın'), ('Diğer', 'Diğer')], blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'in Profili"