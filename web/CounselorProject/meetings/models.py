from django.db import models
from profiles.models import profiles
from characters.models import characters

class meetings(models.Model):
    profile = models.ForeignKey(profiles, on_delete=models.CASCADE)
    character = models.ForeignKey(characters, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    content = models.TextField() # full conversation

    def __str__(self):
        return f"Meetings with {self.user_id} at {self.created_at}"
