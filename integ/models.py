from django.db import models
from django.conf import settings

class UserToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expires_at = models.DateTimeField(null=True, blank=True)  # Optional, if you store token expiration time

    def __str__(self):
        return f"Tokens for {self.user}"