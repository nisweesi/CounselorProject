from django.db import models
from meetings.models import meetings

class tags(models.Model):
    name = models.CharField(max_length=50)

class meetings_tags(models.Model):
    session = models.ForeignKey(meetings, on_delete=models.CASCADE)
    tag = models.ForeignKey(tags, on_delete=models.CASCADE)
