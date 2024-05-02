from django.shortcuts import render

# Create your views here.
def kelola_podcast(request):
    return render(request, "kelola_podcast.html")

def chart_list(request):
    return render(request, "chart_list.html")

def chart_detail(request):
    return render(request, "chart_detail.html")

def play_podcast(request):
    return render(request, "play_podcast.html")

def daftarEpisode_podcast(request):
    return render(request, "daftarEpisode_podcast.html")

def create_episode(request):
    return render(request, "create_episode.html")
