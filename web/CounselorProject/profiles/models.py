from django.db import models

class profiles(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    createdAt = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True)
    sexual_orientation = models.TextField(max_length=50)
    location = models.TextField(max_length=50)
    pronouns = models.CharField(max_length=20)
    education_level = models.CharField(max_length=50)
    occupation = models.CharField(max_length=50)
    political_stand = models.TextField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
