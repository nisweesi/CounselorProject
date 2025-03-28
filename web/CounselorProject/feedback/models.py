from django.db import models
from meetings.models import meetings

class feedback(models.Model):
    name = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    session = models.ForeignKey(meetings, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
