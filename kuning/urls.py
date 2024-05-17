from django.urls import path
from kuning.views import subscribe_menu, subscribe_form, subscribe_history, downloaded_songs, delete_downloaded_song, search_content, search_found

app_name = 'kuning'

urlpatterns = [
    path('subscribe_menu', subscribe_menu, name='subscribe_menu'),
    path('subscribe_form/', subscribe_form, name='subscribe_form'),
    path('subscribe_history/', subscribe_history, name='subscribe_history'),
    path('downloaded_songs/', downloaded_songs, name='downloaded_songs'),
    path('delete_downloaded_song/<str:song_id>/', delete_downloaded_song, name='delete_downloaded_song'),
    path('search_content/', search_content, name='search_content'),
    path('search_found/', search_found, name='search_found'),
]