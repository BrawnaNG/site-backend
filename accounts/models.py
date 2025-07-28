from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from story.models import Story


class User(AbstractUser):
    ALIAS_MAX_LENGTH = 50
    EMAIL_MAX_LENGTH = 254

    # custom user types
    AUTHOR = "author"
    READER = "reader"
    ADMINISTRATOR = "administrator"
    USER_TYPES = [
        (AUTHOR, "Author"),
        (READER, "Reader"),
        (ADMINISTRATOR, "Administrator"),
    ]

    alias = models.CharField(max_length=ALIAS_MAX_LENGTH, unique=True)
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True)
    type = models.CharField(max_length=20, choices=USER_TYPES, default=READER)
    saved_stories = models.ManyToManyField(
        Story, related_name="saved_by_users", blank=True
    )
    old_brawna_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.alias or self.username

    @classmethod
    def generate_activation_token(cls, user_id):
        payload = {"user_id": user_id, "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode(
            "utf-8"
        )
        return token
    
    @classmethod
    def generate_reset_token(cls, user_id):
        payload = {"user_id": user_id, "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode(
            "utf-8"
        )
        return token
