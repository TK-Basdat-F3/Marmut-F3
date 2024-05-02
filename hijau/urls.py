from django.urls import path
from hijau.views import kelola_playlist, detail_playlist, detail_song

app_name = 'hijau'

urlpatterns = [
    path('kelola_playlist/', kelola_playlist, name='kelola_playlist'),
    path('kelola_playlist/detail/', detail_playlist, name='detail-playlist'),
    path('kelola_playlist/detail-song/', detail_song, name='detail-song'),

]