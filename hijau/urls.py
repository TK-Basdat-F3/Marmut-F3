from django.urls import path
from hijau.views import *

app_name = 'hijau'

urlpatterns = [
    path('kelola_playlist/', kelola_playlist, name='kelola_playlist'),
    path('add-playlist/',add_playlist,name='add_playlist'),
    path('edit-playlist/',edit_playlist,name='edit_playlist'),
    path('delete-playlist/<uuid:id_playlist>/',delete_playlist,name='delete_playlist'),

    path('playlist-detail/<uuid:id_playlist>/', playlist_detail, name='playlist_detail'),
    path('playlist-detail/shuffle-play/<uuid:id_user_playlist>/<uuid:id_playlist>/<str:email_pembuat>/', shuffle_play, name='shuffle_play'),

    path('play-song/<uuid:id_song>/',play_song,name='play_song'),

    path('add-song/<uuid:id_playlist>/',add_song,name='add_song'),
    path('add-song-detail/<uuid:id_song>/',add_song_from_detail,name='add_song_from_detail'),

    path('delete-song/<uuid:id_playlist>/<uuid:id_song>/',delete_song,name='delete_song'),

    path('download-song/<uuid:id_song>/',download_song,name='download_song'),
    path('play_user_playlist/<uuid:id_user_playlist>/<uuid:id_song>/', play_user_playlist, name='play_user_playlist'),
    path('song-detail/<uuid:id_song>/', song_detail, name='song_detail'),

]