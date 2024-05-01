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

class Role(models.TextChoices):
    PODCASTER = 'PODCASTER', 'Podcaster'
    ARTIST = 'ARTIST', 'Artist'
    SONGWRITER = 'SONGWRITER', 'Songwriter'

    
# class akun(models.Model):
#     email = models.EmailField(max_length=50, primary_key=True)
#     password = models.CharField(max_length=50)
#     nama = models.CharField(max_length=100)
#     gender = models.IntegerField(choices=((0, 'Perempuan'), (1, 'Laki-laki')))
#     tempat_lahir = models.CharField(max_length=50)
#     tanggal_lahir = models.DateField(default=localdate)
#     is_verified = models.BooleanField()
#     kota_asal = models.CharField(max_length=50)

# class paket(models.Model):
#     jenis = models.CharField(max_length=50, primary_key=True)
#     harga = models.IntegerField()

# class transaction(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     jenis_paket = models.ForeignKey(paket, on_delete=models.CASCADE)
#     email_akun = models.ForeignKey(akun, on_delete=models.CASCADE)
#     timestamp_dimulai = models.DateTimeField()
#     timestamp_berakhir = models.DateTimeField()
#     metode_bayar = models.CharField(max_length=50)
#     nominal = models.IntegerField()

# class premium(models.Model):
#     email = models.OneToOneField(akun, on_delete=models.CASCADE, primary_key=True)

# class nonpremium(models.Model):
#     email = models.OneToOneField(akun, on_delete=models.CASCADE, primary_key=True)

# class konten(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     judul = models.CharField(max_length=100)
#     tanggal_rilis = models.DateField(default=localdate)
#     tahun = models.IntegerField()
#     durasi = models.IntegerField()  # Durasi in minutes

# class genre(models.Model):
#     id_konten = models.OneToOneField(konten, on_delete=models.CASCADE, primary_key=True)
#     genre = models.CharField(max_length=50)

# class podcaster(models.Model):
#     email = models.OneToOneField(akun, on_delete=models.CASCADE, primary_key=True)

# class podcast(models.Model):
#     id_konten = models.OneToOneField(konten, on_delete=models.CASCADE, primary_key=True)
#     email_podcaster = models.ForeignKey(podcaster, on_delete=models.CASCADE)

# class episode(models.Model):
#     id_episode = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     id_konten_podcast = models.ForeignKey(podcast, on_delete=models.CASCADE)
#     judul = models.CharField(max_length=100)
#     deskripsi = models.CharField(max_length=500)
#     durasi = models.IntegerField()  # Durasi in minutes
#     tanggal_rilis = models.DateField(default=localdate)

# class pemilik_hak_cipta(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     rate_royalti = models.IntegerField()

# class artist(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     email_akun = models.ForeignKey(akun, on_delete=models.CASCADE)
#     id_pemilik_hak_cipta = models.ForeignKey(pemilik_hak_cipta, on_delete=models.CASCADE)

# class songwriter(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     email_akun = models.ForeignKey(akun, on_delete=models.CASCADE)
#     id_pemilik_hak_cipta = models.ForeignKey(pemilik_hak_cipta, on_delete=models.CASCADE)

# class album(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     judul = models.CharField(max_length=100)
#     jumlah_lagu = models.IntegerField(default=0)
#     id_label = models.ForeignKey('Label', on_delete=models.CASCADE)
#     total_durasi = models.IntegerField()

# class song(models.Model):
#     id_konten = models.OneToOneField(konten, on_delete=models.CASCADE, primary_key=True)
#     id_artist = models.ForeignKey(artist, on_delete=models.CASCADE)
#     id_album = models.ForeignKey(album, on_delete=models.CASCADE)
#     total_play = models.IntegerField(default=0)
#     total_download = models.IntegerField(default=0)

# class songwriter_write_song(models.Model):
#     id_songwriter = models.ForeignKey(songwriter, on_delete=models.CASCADE)
#     id_song = models.ForeignKey(song, on_delete=models.CASCADE)
#     class Meta:
#         unique_together = (('id_songwriter', 'id_song'),)

# class downloaded_song(models.Model):
#     id_song = models.ForeignKey(song, on_delete=models.CASCADE)
#     email_downloader = models.ForeignKey(premium, on_delete=models.CASCADE)
#     class Meta:
#         unique_together = (('id_song', 'email_downloader'),)

# class label(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     nama = models.CharField(max_length=100)
#     email = models.EmailField(max_length=50)
#     password = models.CharField(max_length=50)
#     kontak = models.CharField(max_length=50)
#     id_pemilik_hak_cipta = models.ForeignKey(pemilik_hak_cipta, on_delete=models.CASCADE)

# class playlist(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

# class chart(models.Model):
#     tipe = models.CharField(max_length=50, primary_key=True)
#     id_playlist = models.ForeignKey(playlist, on_delete=models.CASCADE)

# class user_playlist(models.Model):
#     email_pembuat = models.ForeignKey(akun, on_delete=models.CASCADE)
#     id_user_playlist = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     judul = models.CharField(max_length=100)
#     deskripsi = models.CharField(max_length=500)
#     jumlah_lagu = models.IntegerField()
#     tanggal_dibuat = models.DateField(default=localdate)
#     id_playlist = models.ForeignKey(playlist, on_delete=models.CASCADE)
#     total_durasi = models.IntegerField()

# class royalti(models.Model):
#     id_pemilik_hak_cipta = models.ForeignKey(pemilik_hak_cipta, on_delete=models.CASCADE)
#     id_song = models.ForeignKey(song, on_delete=models.CASCADE)
#     jumlah = models.IntegerField()

# class akun_play_user_playlist(models.Model):
#     email_pemain = models.ForeignKey(akun, on_delete=models.CASCADE)
#     id_user_playlist = models.ForeignKey(user_playlist, on_delete=models.CASCADE, related_name='plays')
#     waktu = models.DateTimeField(primary_key=True)

# class akun_play_song(models.Model):
#     email_pemain = models.ForeignKey(akun, on_delete=models.CASCADE)
#     id_song = models.ForeignKey(song, on_delete=models.CASCADE)
#     waktu = models.DateTimeField(primary_key=True)

# class playlist_song(models.Model):
#     id_playlist = models.ForeignKey(playlist, on_delete=models.CASCADE)
#     id_song = models.ForeignKey(song, on_delete=models.CASCADE)
#     class Meta:
#         unique_together = (('id_playlist', 'id_song'),)