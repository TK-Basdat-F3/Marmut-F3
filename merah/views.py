from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from main.models import album, artist, genre, song, label, songwriter, royalti

# Views fro artist/songwriter manage album and song
# @login_required
# def manage_album_song(request):
#     albums = album.objects.filter(artist=request.user.artist)
#     labels = label.objects.all()
#     return render(request, 'manage_album_song.html', {'albums': albums, 'labels': labels})

# @login_required
# def create_album(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         label_id = request.POST.get('label')
#         label = label.objects.get(id=label_id)
#         album.objects.create(title=title, label=label, artist=request.user.artist)
#     return redirect('manage')

# @login_required
# def create_song(request):
#     if request.method == 'POST':
#         album_id = request.POST['album_id']
#         title = request.POST['title']
#         duration = request.POST['duration']
#         artist_id = request.POST.get('artist')  
#         songwriter_ids = request.POST.getlist('songwriters')
#         genre_ids = request.POST.getlist('genres')

#         album = album.objects.get(id=album_id)
#         artist = request.user.artist if request.user.is_artist else Artist.objects.get(id=artist_id)
        
#         song = song.objects.create(
#             title=title,
#             artist=artist,
#             album=album,
#             duration=duration
#         )
        
#         for songwriter_id in songwriter_ids:
#             songwriter = songwriter.objects.get(id=songwriter_id)
#             song.songwriters.add(songwriter)
        
#         for genre_id in genre_ids:
#             genre = genre.objects.get(id=genre_id)
#             song.genres.add(genre)
#         song.save()

#         return redirect('manage_album', album_id=album_id)  
#     else:
#         pass

# @login_required
# def delete_album(request, album_id):
#     album.objects.get(id=album_id).delete()
#     return redirect('manage')

# @login_required
# def delete_song(request, song_id):
#     song.objects.get(id=song_id).delete()
#     return redirect('manage')

# @login_required
# def add_song_to_album(request, album_id):
#     album = album.objects.get(id=album_id)
#     artists = artist.objects.all() 
#     songwriters = songwriter.objects.all()  
#     genres = genre.objects.all()  
#     return render(request, 'add_song_to_album.html', {
#         'album': album,
#         'artists': artists,
#         'songwriters': songwriters,
#         'genres': genres,
#     })

# # Views for Check Royalty

# @login_required
# def check_royalties(request):
#     royalties = royalti.objects.filter(owner=request.user).select_related('song', 'song__album')
    
#     context = {
#         'royalties': [
#             {
#                 'song_title': royalty.song.title,
#                 'album_title': royalty.song.album.title,
#                 'total_plays': royalty.song.total_plays,
#                 'total_downloads': royalty.song.total_downloads,
#                 'total_royalties': royalty.amount
#             } for royalty in royalties
#         ]
#     }
    
#     return render(request, 'check_royalties.html', context)

# # Views for Label Manage Album and Song

# @login_required
# def manage_label_albums_songs(request):
#     # Ensure you only show albums managed by the logged-in label
#     albums = album.objects.filter(label=request.user.labelprofile)
#     return render(request, 'manage_label_albums_songs.html', {'albums': albums})

# @login_required
# def label_view_songs(request, album_id):
#     album = get_object_or_404(album, id=album_id, label=request.user.labelprofile)
#     songs = album.songs.all()
#     return render(request, 'label_view_songs.html', {'album': album, 'songs': songs})

# @login_required
# def label_delete_album(request, album_id):
#     album = get_object_or_404(album, id=album_id, label=request.user.labelprofile)
#     album.delete()
#     return redirect('manage_label_albums_songs')


def manage_albums(request):
    return render(request, 'artist_manage_album_song.html')

def cek_royalti(request):
    return render(request, 'cek_royalti.html')

def label_manage(request):
    return render(request, 'label_manage_album_song.html')