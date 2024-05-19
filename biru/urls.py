
from django.urls import path
from biru.views import kelola_podcast, play_podcast, daftar_episode, chart_list, chart_detail, create_episode, create_podcast, delete_episode, delete_podcast

app_name = 'biru'

urlpatterns = [
    path('kelola_podcast/', kelola_podcast, name='kelola_podcast'),
    path('chart_list/', chart_list, name='chart_list'),
    path('chart_detail/<uuid:id_chart>/<str:nama_chart>/', chart_detail, name='chart_detail'),
    path('play_podcast/<uuid:id_podcast>/', play_podcast, name='play_podcast'),
    path('daftar_episode/<uuid:id_podcast>/', daftar_episode, name='daftar_episode'),
    path('create_episode/<uuid:id_podcast>/', create_episode, name='create_episode'),
    path('delete_episode/<uuid:id_podcast>/', delete_episode, name='delete_episode'),
    path('delete_podcast/<uuid:id_podcast>/', delete_podcast, name='delete_podcast'),
    path('create_podcast/', create_podcast, name='create_podcast'),
]