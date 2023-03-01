from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    slack_webhook_url = models.URLField(blank=True, null=True, default=None)
