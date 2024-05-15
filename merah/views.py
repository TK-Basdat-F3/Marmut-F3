from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from main.supabase_client import get_supabase
from django.views.decorators.csrf import csrf_exempt
from utilities.helper import query
from django.http.response import JsonResponse
import uuid

def manage_albums(request):
    labels = query('SELECT id, nama FROM "MARMUT"."label"')
    albums = query('''
        SELECT 
            album.id,
            album.judul,
            album.jumlah_lagu,
            album.total_durasi,
            label.nama as label_nama
        FROM "MARMUT"."album"
        JOIN "MARMUT"."label" ON album.id_label = label.id
    ''')
    if type(labels) != list:
        labels = []
    if type(albums) != list:
        albums = []
    return render(request, 'artist_manage_album_song.html', {'labels': labels, 'albums': albums})


def cek_royalti(request):
    return render(request, 'cek_royalti.html')

def label_manage(request):
    return render(request, 'label_manage_album_song.html')

@csrf_exempt
def create_album(request):
    if request.method == 'POST':
        judul_album = request.POST.get('judul_album')
        label = request.POST.get('label')
        id_album = str(uuid.uuid4())

        create_album_query = f"""
        INSERT INTO "MARMUT"."album" (id, judul, jumlah_lagu, id_label, total_durasi)
        VALUES ('{id_album}', '{judul_album}', 0, '{label}', 0)
        """
        result = query(create_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return redirect('merah:add_song', id_album=id_album)

    labels = query('SELECT id, nama FROM "MARMUT"."label"')
    albums = query('SELECT * FROM "MARMUT"."album"')
    if type(labels) != list:
        labels = []
    if type(albums) != list:
        albums = []
    return render(request, 'artist_manage_album_song.html', {'labels': labels, 'albums': albums})

@csrf_exempt
def add_song(request, id_album):
    if request.method == 'POST':
        judul_lagu = request.POST.get('judul_lagu')
        artist = request.POST.get('artist')
        songwriters = request.POST.getlist('songwriters')
        genres = request.POST.getlist('genres')
        durasi = int(request.POST.get('durasi'))
        id_song = str(uuid.uuid4())

        create_song_query = f"""
        INSERT INTO "MARMUT"."song" (id_konten, id_artist, id_album, total_play, total_download)
        VALUES ('{id_song}', '{artist}', '{id_album}', 0, 0)
        """
        result = query(create_song_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        create_konten_query = f"""
        INSERT INTO "MARMUT"."konten" (id, judul, tanggal_rilis, tahun, durasi)
        VALUES ('{id_song}', '{judul_lagu}', CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), {durasi})
        """
        result = query(create_konten_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        for genre in genres:
            create_genre_query = f"""
            INSERT INTO "MARMUT"."genre" (id_konten, genre)
            VALUES ('{id_song}', '{genre}')
            """
            result = query(create_genre_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        for songwriter in songwriters:
            create_songwriter_query = f"""
            INSERT INTO "MARMUT"."songwriter_write_song" (id_songwriter, id_song)
            VALUES ('{songwriter}', '{id_song}')
            """
            result = query(create_songwriter_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        update_album_query = f"""
        UPDATE "MARMUT"."album"
        SET jumlah_lagu = jumlah_lagu + 1, total_durasi = total_durasi + {durasi}
        WHERE id = '{id_album}'
        """
        result = query(update_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return redirect('merah:list_albums')

    artists = query('SELECT id, nama FROM "MARMUT"."artist"')
    songwriters = query('SELECT id, nama FROM "MARMUT"."songwriter"')
    genres = query('SELECT DISTINCT genre FROM "MARMUT"."genre"')
    album = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_album}\'')
    if type(artists) != list:
        artists = []
    if type(songwriters) != list:
        songwriters = []
    if type(genres) != list:
        genres = []
    if type(album) != list or not album:
        album = None
    else:
        album = album[0]
    return render(request, 'add_song.html', {
        'artists': artists,
        'songwriters': songwriters,
        'genres': genres,
        'album': album
    })

def list_albums(request):
    albums = query('SELECT * FROM "MARMUT"."album"')
    return render(request, 'list_albums.html', {'albums': albums})

def album_detail(request, id_album):
    album = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_album}\'')
    songs = query(f'SELECT * FROM "MARMUT"."song" WHERE id_album = \'{id_album}\'')
    return render(request, 'album_detail.html', {'album': album, 'songs': songs})

@csrf_exempt
def delete_album(request, id_album):
    if request.method == 'POST':
        delete_album_query = f'DELETE FROM "MARMUT"."album" WHERE id = \'{id_album}\''
        result = query(delete_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return redirect('list_albums')

    album = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_album}\'')
    return render(request, 'delete_album.html', {'album': album})
