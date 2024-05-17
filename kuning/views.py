from django.db import connection
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from psycopg2 import OperationalError, ProgrammingError
from uuid import UUID
from marmut_f3 import settings
from utilities.helper import query
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def subscribe_menu(request):
    return render(request, "subscribe.html")

def subscribe_form(request):
    return render(request, "subscribe_form.html")

def subscribe_history(request):
    return render(request, "subscribe_history.html")

def downloaded_songs(request):
    username = request.session.get('username')
    print(username)

    if not username:
        return HttpResponseNotFound("User not logged in.")
    
    email_downloader = query(f'SELECT email_downloader FROM "MARMUT"."downloaded_song" WHERE email_downloader = \'{username}\'')
    songs = []

    if email_downloader:
        song_ids = query(f'SELECT id_song FROM "MARMUT"."downloaded_song" WHERE email_downloader = \'{email_downloader[0][0]}\'')
        for song_id in song_ids:
            song_list = []
            song = query(f'''
                        SELECT k.judul, a.nama
                        FROM "MARMUT"."downloaded_song" ds
                        JOIN "MARMUT"."konten" k ON ds.id_song = k.id
                        JOIN "MARMUT"."song" s ON k.id = s.id_konten
                        JOIN "MARMUT"."artist" art ON s.id_artist = art.id
                        JOIN "MARMUT"."akun" a ON art.email_akun = a.email
                        WHERE ds.id_song = \'{song_id[0]}\'
                        ''')[0]
            song_list.append(str(song_id[0]))
            song_list.append(song.judul)
            song_list.append(song.nama)
            songs.append(song_list)
    request.session['downloaded_songs'] = songs
    return render(request, "downloaded_songs.html")

@csrf_exempt
def delete_downloaded_song(request, song_id):
    print("song_id: ", song_id)
    username = request.session.get('username')
    if not username:
        return HttpResponseNotFound("User not logged in.")

    if request.method == 'POST':
        query(f'DELETE FROM "MARMUT"."downloaded_song" WHERE id_song = \'{song_id}\' AND email_downloader = \'{username}\'')
        return redirect('kuning:downloaded_songs')
    
    songs = downloaded_songs(request)
    return render(request, 'downloaded_songs.html', {'songs': songs})

def search_content(request):
    results = []
    query_str = request.GET.get('q')
    if query_str:
        songs = query(f'''
                           SELECT k.judul, a.nama
                           FROM "MARMUT"."konten" k
                           JOIN "MARMUT"."song" s ON k.id = s.id_konten
                           JOIN "MARMUT"."artist" art ON s.id_konten = art.id
                           JOIN "MARMUT"."akun" a ON art.email_akun = a.email
                           WHERE LOWER(k.judul) LIKE LOWER(\'%{query_str}%\')
                        ''')
        podcasts = query(f'''
                           SELECT k.judul, a.nama
                           FROM "MARMUT"."konten" k
                           JOIN "MARMUT"."podcast" p ON k.id = p.id_konten
                           JOIN "MARMUT"."podcaster" pr ON p.email_podcaster = pr.email
                           JOIN "MARMUT"."akun" a ON pr.email = a.email
                           WHERE LOWER(k.judul) LIKE LOWER(\'%{query_str}%\')
                        ''')
        playlists = query(f'''
                           SELECT up.judul, a.nama 
                           FROM "MARMUT"."user_playlist" up
                           JOIN "MARMUT"."akun" a ON up.email_pembuat = a.email
                           WHERE LOWER(up.judul) LIKE LOWER(\'%{query_str}%\')
                        ''')
        results.append(songs)
        results.append(podcasts)
        results.append(playlists)
    else:
        results = None
    return render(request, 'search_content.html', {'results': results})

def search_found(request):
    results = []
    query_str = request.GET.get('q')
    if query_str:
        query_lower = query_str.lower()
        songs = query(f'''
                           SELECT k.judul, a.nama
                           FROM "MARMUT"."konten" k
                           JOIN "MARMUT"."song" s ON k.id = s.id_konten
                           JOIN "MARMUT"."artist" art ON s.id_artist = art.id
                           JOIN "MARMUT"."akun" a ON art.email_akun = a.email
                           WHERE LOWER(k.judul) LIKE \'%{query_str}%\'
                        ''')
        podcasts = query(f'''
                           SELECT k.judul, a.nama
                           FROM "MARMUT"."konten" k
                           JOIN "MARMUT"."podcast" p ON k.id = p.id_konten
                           JOIN "MARMUT"."podcaster" pr ON p.email_podcaster = pr.email
                           JOIN "MARMUT"."akun" a ON pr.email = a.email
                           WHERE LOWER(k.judul) LIKE \'%{query_str}%\'
                        ''')
        playlists = query(f'''
                           SELECT up.judul, a.nama 
                           FROM "MARMUT"."user_playlist" up
                           JOIN "MARMUT"."akun" a ON up.email_pembuat = a.email
                           WHERE LOWER(up.judul) LIKE \'%{query_str}%\'
                        ''')
        results.append(songs)
        results.append(podcasts)
        results.append(playlists)
        print(len(songs))
        print(len(podcasts))
        print(len(playlists))
    else:
        results = None
    return render(request, 'search_found.html', {'results': results, 'query': query_str})
