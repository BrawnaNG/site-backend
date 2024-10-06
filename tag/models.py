from django.conf import settings
from django.db import models


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    old_brawna_term_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
