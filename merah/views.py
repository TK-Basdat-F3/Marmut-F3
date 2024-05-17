from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from utilities.helper import query, get_user_type
from django.http.response import JsonResponse
import uuid

def has_role(request, required_roles):
    user_roles = request.session.get('roles', [])
    return any(role in user_roles for role in required_roles)

@login_required
def manage_albums(request):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

    labels = query('SELECT id, nama FROM "MARMUT"."label"')
    albums = query('''
        SELECT 
            album.id,
            album.judul,
            COUNT(song.id_konten) AS jumlah_lagu,
            COALESCE(SUM(konten.durasi), 0) AS total_durasi,
            label.nama as label_nama
        FROM "MARMUT"."album" AS album
        LEFT JOIN "MARMUT"."song" AS song ON album.id = song.id_album
        LEFT JOIN "MARMUT"."konten" AS konten ON song.id_konten = konten.id
        JOIN "MARMUT"."label" AS label ON album.id_label = label.id
        GROUP BY album.id, label.nama
    ''')
    if type(labels) != list:
        labels = []
    if type(albums) != list:
        albums = []
    return render(request, 'artist_manage_album_song.html', {'labels': labels, 'albums': albums})

@login_required
def cek_royalti(request):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
        return redirect('main:login')

    email = request.user.email
    user_type = get_user_type(email)

    if user_type == 'artist' or user_type == 'songwriter':
        query_royalti = f"""
            SELECT k.judul AS judul_lagu, a.judul AS judul_album, s.total_play, s.total_download, 
            (p.rate_royalti * s.total_play) AS total_royalti
            FROM "MARMUT"."konten" k
            JOIN "MARMUT"."song" s ON k.id = s.id_konten
            JOIN "MARMUT"."album" a ON s.id_album = a.id
            JOIN "MARMUT"."royalti" r ON s.id_konten = r.id_song
            JOIN "MARMUT"."pemilik_hak_cipta" p ON r.id_pemilik_hak_cipta = p.id
            WHERE p.email_akun = '{email}'
        """
    elif user_type == 'label':
        query_royalti = f"""
            SELECT k.judul AS judul_lagu, a.judul AS judul_album, s.total_play, s.total_download, 
            (p.rate_royalti * s.total_play) AS total_royalti
            FROM "MARMUT"."konten" k
            JOIN "MARMUT"."song" s ON k.id = s.id_konten
            JOIN "MARMUT"."album" a ON s.id_album = a.id
            JOIN "MARMUT"."royalti" r ON s.id_konten = r.id_song
            JOIN "MARMUT"."pemilik_hak_cipta" p ON r.id_pemilik_hak_cipta = p.id
            WHERE p.id_label = (SELECT id FROM "MARMUT"."label" WHERE email = '{email}')
        """
    else:
        return render(request, 'cek_royalti.html', {'royalties': []})

    royalties = query(query_royalti)
    return render(request, 'cek_royalti.html', {'royalties': royalties})

@login_required
def label_manage(request):
    if not has_role(request, ['Label']):
        return redirect('main:login')

    return render(request, 'label_manage_album_song.html')

@csrf_exempt
@login_required
def create_album(request):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

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
@login_required
def add_song(request, id_album):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

    if request.method == 'POST':
        judul_lagu = request.POST.get('judul_lagu')
        artist = request.POST.get('artist')
        songwriters = request.POST.getlist('songwriters')
        genres = request.POST.getlist('genres')
        durasi = int(request.POST.get('durasi'))
        id_song = str(uuid.uuid4())

        # Insert into KONTEN first
        create_konten_query = f"""
        INSERT INTO "MARMUT"."konten" (id, judul, tanggal_rilis, tahun, durasi)
        VALUES ('{id_song}', '{judul_lagu}', CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), {durasi})
        """
        result = query(create_konten_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Insert into SONG next
        create_song_query = f"""
        INSERT INTO "MARMUT"."song" (id_konten, id_artist, id_album, total_play, total_download)
        VALUES ('{id_song}', '{artist}', '{id_album}', 0, 0)
        """
        result = query(create_song_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Insert genres
        for genre in genres:
            create_genre_query = f"""
            INSERT INTO "MARMUT"."genre" (id_konten, genre)
            VALUES ('{id_song}', '{genre}')
            """
            result = query(create_genre_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Insert songwriters
        for songwriter in songwriters:
            create_songwriter_query = f"""
            INSERT INTO "MARMUT"."songwriter_write_song" (id_songwriter, id_song)
            VALUES ('{songwriter}', '{id_song}')
            """
            result = query(create_songwriter_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Update album's song count and duration
        update_album_query = f"""
        UPDATE "MARMUT"."album"
        SET jumlah_lagu = jumlah_lagu + 1, total_durasi = total_durasi + {durasi}
        WHERE id = '{id_album}'
        """
        result = query(update_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return JsonResponse({'success': 'true', 'message': f'{judul_lagu} successfully added to album!'})

    artists = query('''
        SELECT artist.id, akun.nama 
        FROM "MARMUT"."artist" 
        JOIN "MARMUT"."akun" ON artist.email_akun = akun.email
    ''')
    songwriters = query('''
        SELECT songwriter.id, akun.nama 
        FROM "MARMUT"."songwriter" 
        JOIN "MARMUT"."akun" ON songwriter.email_akun = akun.email
    ''')
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

@login_required
def list_albums(request):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
        return redirect('main:login')

    albums = query('SELECT * FROM "MARMUT"."album"')
    return render(request, 'list_albums.html', {'albums': albums})

@login_required
def album_detail(request, id_album):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
        return redirect('main:login')

    album_query = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_album}\'')
    if not album_query:
        return JsonResponse({'success': 'false', 'message': 'Album not found'}, status=404)
    album = album_query[0]

    songs_query = query(f'''
        SELECT 
            song.id_konten, 
            konten.judul, 
            konten.durasi, 
            song.total_play, 
            song.total_download 
        FROM "MARMUT"."song"
        JOIN "MARMUT"."konten" ON song.id_konten = konten.id
        WHERE song.id_album = '{id_album}'
    ''')

    return render(request, 'album_detail.html', {
        'album': album,
        'songs': songs_query
    })

@csrf_exempt
@login_required
def delete_album(request, id_album):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

    if request.method == 'POST':
        delete_album_query = f'DELETE FROM "MARMUT"."album" WHERE id = \'{id_album}\''
        result = query(delete_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return redirect('merah:manage_albums')

    album = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_album}\'')
    return render(request, 'delete_album.html', {'album': album})

@csrf_exempt
@login_required
def delete_song(request, id_song):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

    if request.method == 'POST':
        album_id = request.POST.get('id_album')

        # Check if song ID is valid before deleting
        song_query = query(f'SELECT * FROM "MARMUT"."song" WHERE id_konten = \'{id_song}\'')
        if not song_query:
            return JsonResponse({'success': 'false', 'message': 'Song not found'}, status=404)

        # Get song duration before deleting
        song_duration = query(f'SELECT durasi FROM "MARMUT"."konten" WHERE id = \'{id_song}\'')[0][0]

        # Delete the song
        delete_song_query = f'DELETE FROM "MARMUT"."song" WHERE id_konten = \'{id_song}\''
        result = query(delete_song_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Update album's song count and duration
        update_album_query = f"""
        UPDATE "MARMUT"."album"
        SET jumlah_lagu = jumlah_lagu - 1, 
            total_durasi = total_durasi - {song_duration}
        WHERE id = '{album_id}'
        """
        result = query(update_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return redirect('merah:album_detail', id_album=album_id)

    return JsonResponse({'success': 'false', 'message': 'Invalid request method'}, status=400)