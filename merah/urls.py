
from django.urls import path
from . import views


app_name = 'merah'

urlpatterns = [
    path('manage-albums/', views.manage_albums, name='manage_albums'),
    path('cek-royalti/', views.cek_royalti, name='cek-royalti'),
    path('label-manage/', views.label_manage, name='label-manage'),
    path('create_album/', views.create_album, name='create_album'),
    path('add_song/<uuid:id_album>/', views.add_song, name='add_song'),
    path('list_albums/', views.list_albums, name='list_albums'),
    path('album_detail/<uuid:id_album>/', views.album_detail, name='album_detail'),
    path('delete_album/<uuid:id_album>/', views.delete_album, name='delete_album'),
]