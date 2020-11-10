from django.db import models

# Create your models here.


class Candidate(models.Model):
    filename = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default=None, null=True)

    def __str__(self):
        return self.name
