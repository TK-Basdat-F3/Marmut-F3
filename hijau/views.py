from django.shortcuts import render

# Create your views here.
def kelola_playlist(request):
    return render(request, "kelola_playlist.html")

def detail_playlist(request):
    return render(request, "detail_playlist.html")

def detail_song(request):
    return render(request, "detail_song.html")