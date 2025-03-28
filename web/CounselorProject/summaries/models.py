from django.db import models
from profiles.models import profiles

class summaries(models.Model):
    profile = models.OneToOneField(profiles, on_delete=models.CASCADE)
    updatedAt = models.DateTimeField(auto_now=True)
    profile_summary = models.TextField(blank=True)

    def __str__(self):
        return f"Summary for {self.profile.first_name} {self.profile.last_name}"
