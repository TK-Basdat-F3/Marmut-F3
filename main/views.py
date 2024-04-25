from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Album, Artist, Genre, Song, Label, Songwriter

@login_required(login_url='/login')
def show_main(request):
    context = {
        'class': 'basdat f',
        'last_login': request.COOKIES['last_login'],
    }

    return render(request, "main.html", context)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main")) 
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
    context = {}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

@login_required
def manage_album_song(request):
    albums = Album.objects.filter(artist=request.user.artist)
    labels = Label.objects.all()
    return render(request, 'manage_album_song.html', {'albums': albums, 'labels': labels})

@login_required
def create_album(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        label_id = request.POST.get('label')
        label = Label.objects.get(id=label_id)
        Album.objects.create(title=title, label=label, artist=request.user.artist)
    return redirect('manage')

@login_required
def create_song(request):
    if request.method == 'POST':
        album_id = request.POST['album_id']
        title = request.POST['title']
        duration = request.POST['duration']
        artist_id = request.POST.get('artist')  # Only provided if user is a songwriter
        songwriter_ids = request.POST.getlist('songwriters')
        genre_ids = request.POST.getlist('genres')

        album = Album.objects.get(id=album_id)
        artist = request.user.artist if request.user.is_artist else Artist.objects.get(id=artist_id)
        
        song = Song.objects.create(
            title=title,
            artist=artist,
            album=album,
            duration=duration
        )
        
        for songwriter_id in songwriter_ids:
            songwriter = Songwriter.objects.get(id=songwriter_id)
            song.songwriters.add(songwriter)
        
        for genre_id in genre_ids:
            genre = Genre.objects.get(id=genre_id)
            song.genres.add(genre)
        song.save()

        return redirect('manage_album', album_id=album_id)  # Redirect to the album management page
    else:
        pass

@login_required
def delete_album(request, album_id):
    Album.objects.get(id=album_id).delete()
    return redirect('manage')

@login_required
def delete_song(request, song_id):
    Song.objects.get(id=song_id).delete()
    return redirect('manage')

@login_required
def add_song_to_album(request, album_id):
    album = Album.objects.get(id=album_id)
    artists = Artist.objects.all()  # Replace with your logic to get artists
    songwriters = Songwriter.objects.all()  # Replace with your logic to get songwriters
    genres = Genre.objects.all()  # Replace with your logic to get genres
    return render(request, 'add_song_to_album.html', {
        'album': album,
        'artists': artists,
        'songwriters': songwriters,
        'genres': genres,
    })
