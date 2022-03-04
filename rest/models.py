from django.db import models


# Create your models here.

class TaskModel(models.Model):
    task = models.CharField(max_length=200, blank=False)
    completed = models.BooleanField(default=False)
