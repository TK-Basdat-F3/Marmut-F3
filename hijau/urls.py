from django.urls import path
from hijau.views import kelola_playlist, detail_playlist, detail_song, play_user_playlist

app_name = 'hijau'

urlpatterns = [
    path('kelola_playlist/', kelola_playlist, name='kelola_playlist'),
    path('kelola_playlist/detail/', detail_playlist, name='detail-playlist'),
    path('kelola_playlist/detail-song/', detail_song, name='detail-song'),
    path('play_user_playlist/<uuid:id_user_playlist>/<uuid:id_song>/', play_user_playlist, name='play_user_playlist')

]