from django.db import models
from meetings.models import meetings

class records(models.Model):
    meeting = models.ForeignKey(meetings, on_delete=models.CASCADE, related_name="records")
    created_at = models.DateTimeField()
    speaker = models.TextField(max_length=10) # "User" or "Charisma:"
    content = models.TextField()

    def __str__(self):
        return f"{self.speaker} at {self.created_at}"
