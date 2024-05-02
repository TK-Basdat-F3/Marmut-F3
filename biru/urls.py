
from django.urls import path
from biru.views import kelola_podcast, play_podcast, daftarEpisode_podcast, chart_list, chart_detail, create_episode

app_name = 'biru'

urlpatterns = [
    path('kelola_podcast/', kelola_podcast, name='kelola_podcast'),
    path('chart_list/', chart_list, name='chart_list'),
    path('chart_detail/', chart_detail, name='chart_detail'),
    path('play_podcast/', play_podcast, name='play_podcast'),
    path('daftarEpisode_podcast/', daftarEpisode_podcast, name='daftarEpisode_podcast'),
    path('create_episode/', create_episode, name='create_episode'),
]