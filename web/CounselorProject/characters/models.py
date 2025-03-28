from django.db import models

class characters(models.Model):
    tone = models.TextField()
    background = models.TextField()

    def __str__(self):
        return f"Character tone: {self.tone}"
