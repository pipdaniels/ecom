from django.db import models
from store import models


# Create your models here.

class messages(models.Model):
    user = models.ForeignKey(Customer, on_delete=Models.CASCADE)
    email = models.ForeignKey(Customer, null=False)
    message = models.TextField()
    date_sent = models.DateTimeField()

    class Meta:
        ordering = [-date_sent]
