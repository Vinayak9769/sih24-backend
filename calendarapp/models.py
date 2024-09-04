from django.conf import settings
from django.db import models
from core.models import Mentor,Mentee
import uuid
from django.contrib.auth import get_user_model


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, limit_choices_to={'is_mentor': True})
    mentee = models.ForeignKey(Mentee, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    theme = models.CharField(
        max_length=20,
        choices=[('Work', 'Work'), ('Personal', 'Personal'), ('Meeting', 'Meeting'), ('Reminders', 'Reminders')],
        default='Personal',
        db_index=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class TemporaryAccessToken(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
