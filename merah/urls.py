
from django.urls import path
from . import views


app_name = 'merah'

urlpatterns = [
    path('manage-albums/', views.manage_albums, name='manage_albums'),
    path('cek-royalti/', views.cek_royalti, name='cek-royalti'),
    path('label-manage/', views.label_manage, name='label-manage'),
    # path('manage_album_song/', views.manage_album_song, name='manage_album_song'),
    # path('create_album/', views.create_album, name='create_album'),
    # path('add_song_to_album/<uuid:album_id>/', views.add_song_to_album, name='add_song_to_album'),
    # path('create_song/', views.create_song, name='create_song'),
    # path('delete_album/<uuid:album_id>/', views.delete_album, name='delete_album'),
    # path('delete_song/<uuid:song_id>/', views.delete_song, name='delete_song'),
    # path('check_royalties/', views.check_royalties, name='check_royalties'),
    #     path('label/manage_albums_songs/', views.manage_label_albums_songs, name='manage_label_albums_songs'),
    # path('label/view_songs/<uuid:album_id>/', views.label_view_songs, name='label_view_songs'),
    # path('label/delete_album/<uuid:album_id>/', views.label_delete_album, name='label_delete_album'),
]