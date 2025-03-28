from django.db import models
from characters.models import characters

class sys_prompt(models.Model):
    name = models.CharField(max_length=100)
    template = models.TextField(max_length=6000)
    character = models.OneToOneField(characters, on_delete=models.CASCADE)

    def __str__(self):
        return f"the character of the voice {self.character}: System Prompt {self.name}"
