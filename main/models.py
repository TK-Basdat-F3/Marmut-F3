from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    nama = models.CharField(max_length=150, verbose_name='Nama')
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Gender')
    tempat_lahir = models.CharField(max_length=100, verbose_name='Tempat Lahir')
    tanggal_lahir = models.DateField(verbose_name='Tanggal Lahir')
    kota_asal = models.CharField(max_length=100, verbose_name='Kota Asal')
    role_podcaster = models.BooleanField(default=False, verbose_name='Podcaster')
    role_artist = models.BooleanField(default=False, verbose_name='Artist')
    role_songwriter = models.BooleanField(default=False, verbose_name='Songwriter')

    def get_roles(self):
        roles = []
        if self.role_podcaster:
            roles.append('Podcaster')
        if self.role_artist:
            roles.append('Artist')
        if self.role_songwriter:
            roles.append('Songwriter')
        return roles
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

class CustomLabel(AbstractUser):
    nama = models.CharField(max_length=150, verbose_name='Nama')
    kontak = models.CharField(max_length=50, verbose_name='Kontak')
    groups = models.ManyToManyField(Group, related_name='custom_label_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_label_permissions')

class Role(models.TextChoices):
    PODCASTER = 'PODCASTER', 'Podcaster'
    ARTIST = 'ARTIST', 'Artist'
    SONGWRITER = 'SONGWRITER', 'Songwriter'
