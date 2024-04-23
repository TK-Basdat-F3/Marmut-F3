from django.db import models

class Akun(models.Model):
    name = models.CharField(max_length=255)
    date_added = models.DateField(auto_now_add=True)