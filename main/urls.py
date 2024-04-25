
from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.show_main, name='show_main'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('manage_album_song/', views.manage_album_song, name='manage_album_song'),
    path('create_album/', views.create_album, name='create_album'),
    path('add_song_to_album/<uuid:album_id>/', views.add_song_to_album, name='add_song_to_album'),
    path('create_song/', views.create_song, name='create_song'),
    path('delete_album/<uuid:album_id>/', views.delete_album, name='delete_album'),
    path('delete_song/<uuid:song_id>/', views.delete_song, name='delete_song'),
]