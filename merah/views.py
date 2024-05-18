from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from utilities.helper import query, get_user_type
from django.http.response import JsonResponse
import uuid

def has_role(request, required_roles):
    user_roles = request.session.get('roles', [])
    return any(role in user_roles for role in required_roles)

def manage_albums(request):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

    # Debugging: Check the session roles
    print(f"Session roles: {request.session.get('roles')}")

    # Fetch labels and albums from the database
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
        LEFT JOIN "MARMUT"."label" AS label ON album.id_label = label.id
        GROUP BY album.id, label.nama
    ''')

    # Debugging: Check the fetched data
    print(f"Labels: {labels}")
    print(f"Albums: {albums}")

    if type(labels) != list:
        labels = []
    if type(albums) != list:
        albums = []

    return render(request, 'artist_manage_album_song.html', {'labels': labels, 'albums': albums})

@csrf_exempt
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

        # Debugging: Print session data
        print(f"Session Data: {dict(request.session.items())}")

        # Add the logged-in songwriter if the user is a songwriter
        if 'Songwriter' in request.session.get('roles', []):
            songwriter_email = request.session.get('email')
            songwriter_id_query = query(f"SELECT id FROM \"MARMUT\".\"songwriter\" WHERE email_akun = '{songwriter_email}'")
            if songwriter_id_query and type(songwriter_id_query) == list:
                songwriter_id = songwriter_id_query[0][0]
                songwriters.append(str(songwriter_id))

        # Get artist ID if user is an artist
        if 'Artist' in request.session.get('roles', []):
            artist_email = request.session.get('email')
            artist_id_query = query(f"SELECT id FROM \"MARMUT\".\"artist\" WHERE email_akun = '{artist_email}'")
            if artist_id_query and type(artist_id_query) == list:
                artist = artist_id_query[0][0]

        # Debugging: Print values
        print(f"Judul Lagu: {judul_lagu}")
        print(f"Artist ID: {artist}")
        print(f"Songwriters: {songwriters}")
        print(f"Genres: {genres}")
        print(f"Durasi: {durasi}")
        print(f"ID Song: {id_song}")

        # Insert into KONTEN first
        create_konten_query = f"""
        INSERT INTO "MARMUT"."konten" (id, judul, tanggal_rilis, tahun, durasi)
        VALUES ('{id_song}', '{judul_lagu}', CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), {durasi})
        """
        print(f"Executing create_konten_query: {create_konten_query}")
        result = query(create_konten_query)
        if type(result) != int:
            print(f"Error inserting into konten: {result}")
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
        else:
            print(f"Successfully inserted into konten: {result}")

        # Verify insertion into KONTEN
        inserted_konten = query(f"SELECT * FROM \"MARMUT\".\"konten\" WHERE id = '{id_song}'")
        print(f"Inserted Konten: {inserted_konten}")

        # Insert into SONG next
        create_song_query = f"""
        INSERT INTO "MARMUT"."song" (id_konten, id_artist, id_album, total_play, total_download)
        VALUES ('{id_song}', '{artist}', '{id_album}', 0, 0)
        """
        print(f"Executing create_song_query: {create_song_query}")
        result = query(create_song_query)
        if type(result) != int:
            print(f"Error inserting into song: {result}")
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
        else:
            print(f"Successfully inserted into song: {result}")

        # Verify insertion into SONG
        inserted_song = query(f"SELECT * FROM \"MARMUT\".\"song\" WHERE id_konten = '{id_song}'")
        print(f"Inserted Song: {inserted_song}")

        # Insert genres
        for genre in genres:
            create_genre_query = f"""
            INSERT INTO "MARMUT"."genre" (id_konten, genre)
            VALUES ('{id_song}', '{genre}')
            """
            print(f"Executing create_genre_query: {create_genre_query}")
            result = query(create_genre_query)
            if type(result) != int:
                print(f"Error inserting into genre: {result}")
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
            else:
                print(f"Successfully inserted into genre: {result}")

            # Verify insertion into GENRE
            inserted_genre = query(f"SELECT * FROM \"MARMUT\".\"genre\" WHERE id_konten = '{id_song}' AND genre = '{genre}'")
            print(f"Inserted Genre: {inserted_genre}")

        # Insert songwriters
        for songwriter in songwriters:
            create_songwriter_query = f"""
            INSERT INTO "MARMUT"."songwriter_write_song" (id_songwriter, id_song)
            VALUES ('{songwriter}', '{id_song}')
            """
            print(f"Executing create_songwriter_query: {create_songwriter_query}")
            result = query(create_songwriter_query)
            if type(result) != int:
                print(f"Error inserting into songwriter_write_song: {result}")
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
            else:
                print(f"Successfully inserted into songwriter_write_song: {result}")

            # Verify insertion into SONGWRITER_WRITE_SONG
            inserted_songwriter = query(f"SELECT * FROM \"MARMUT\".\"songwriter_write_song\" WHERE id_songwriter = '{songwriter}' AND id_song = '{id_song}'")
            print(f"Inserted Songwriter: {inserted_songwriter}")

        # Update album's song count and duration
        update_album_query = f"""
        UPDATE "MARMUT"."album"
        SET jumlah_lagu = jumlah_lagu + 1, total_durasi = total_durasi + {durasi}
        WHERE id = '{id_album}'
        """
        print(f"Executing update_album_query: {update_album_query}")
        result = query(update_album_query)
        if type(result) != int:
            print(f"Error updating album: {result}")
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
        else:
            print(f"Successfully updated album: {result}")

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

def cek_royalti(request):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
        return redirect('main:login')

    email = request.session.get('email')
    user_type = get_user_type(email)
    
    print(f"User type: {user_type}, Email: {email}")

    if user_type == 'artist' or user_type == 'songwriter':
        query_royalti = f"""
            SELECT k.judul AS judul_lagu, a.judul AS judul_album, s.total_play, s.total_download, 
            (p.rate_royalti * s.total_play) AS total_royalti
            FROM "MARMUT"."konten" k
            JOIN "MARMUT"."song" s ON k.id = s.id_konten
            JOIN "MARMUT"."album" a ON s.id_album = a.id
            JOIN "MARMUT"."royalti" r ON s.id_konten = r.id_song
            JOIN "MARMUT"."pemilik_hak_cipta" p ON r.id_pemilik_hak_cipta = p.id
            JOIN "MARMUT"."artist" art ON p.id = art.id_pemilik_hak_cipta
            JOIN "MARMUT"."akun" ak ON ak.email = '{email}'
            WHERE ak.email = '{email}'
        """
    elif user_type == 'label':
        label_id_query = f"SELECT id FROM \"MARMUT\".\"label\" WHERE email = '{email}'"
        label_id = query(label_id_query)[0][0] 

        query_royalti = f"""
            SELECT 
                s.id_konten, 
                k.judul AS judul_lagu, 
                a.judul AS judul_album, 
                s.total_play, 
                s.total_download,
                (p.rate_royalti * s.total_play) AS total_royalti
            FROM "MARMUT"."song" s
            JOIN "MARMUT"."konten" k ON s.id_konten = k.id
            JOIN "MARMUT"."album" a ON s.id_album = a.id
            JOIN "MARMUT"."label" l ON a.id_label = l.id
            JOIN "MARMUT"."pemilik_hak_cipta" p ON l.id_pemilik_hak_cipta = p.id
            WHERE a.id_label = '{label_id}';
        """
    else:
        return render(request, 'cek_royalti.html', {'royalties': [], 'error_message': 'User type not recognized.'})

    try:
        print(f"Executing query: {query_royalti}")
        royalties = query(query_royalti)
        print(f"Query results: {royalties}")
        if not royalties:
            royalties = []
    except Exception as e:
        print(f"Error executing query: {e}")
        royalties = []
        error_message = f"Error executing query: {e}"
        return render(request, 'cek_royalti.html', {'royalties': royalties, 'error_message': error_message})

    return render(request, 'cek_royalti.html', {'royalties': royalties})


def label_manage(request):
    # Debug
    print("Session Data in label_manage:", request.session.items())
    print("User authenticated:", request.user.is_authenticated)
    
    if not has_role(request, ['Label']):
        return redirect('main:login')

    email = request.session.get('email')

    albums_query = f'''
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
        WHERE label.email = '{email}'
        GROUP BY album.id, label.nama
    '''

    albums = query(albums_query)
    if type(albums) != list:
        albums = []

    return render(request, 'label_manage_album_song.html', {'albums': albums})

@csrf_exempt
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
def add_song(request, id_album):
    if not has_role(request, ['Artist', 'Songwriter']):
        return redirect('main:login')

    if request.method == 'POST':
        judul_lagu = request.POST.get('judul_lagu')
        artist = request.POST.get('artist')  # This should hold the artist's ID
        songwriters = request.POST.getlist('songwriters')
        genres = request.POST.getlist('genres')
        durasi = int(request.POST.get('durasi'))
        id_song = str(uuid.uuid4())

        # Debugging: Print session data
        print(f"Session Data: {request.session.items()}")

        # Add the logged-in songwriter if the user is a songwriter
        if 'Songwriter' in request.session.get('roles', []):
            songwriter_email = request.session.get('email')
            songwriter_id_query = query(f"SELECT id FROM \"MARMUT\".\"songwriter\" WHERE email_akun = '{songwriter_email}'")
            if songwriter_id_query and type(songwriter_id_query) == list:
                songwriter_id = songwriter_id_query[0][0]
                songwriters.append(str(songwriter_id))

        # Get artist ID if user is an artist
        if 'Artist' in request.session.get('roles', []):
            artist_email = request.session.get('email')
            artist_id_query = query(f"SELECT id FROM \"MARMUT\".\"artist\" WHERE email_akun = '{artist_email}'")
            if artist_id_query and type(artist_id_query) == list:
                artist = artist_id_query[0][0]

        # Debugging: Print values
        print(f"Judul Lagu: {judul_lagu}")
        print(f"Artist ID: {artist}")
        print(f"Songwriters: {songwriters}")
        print(f"Genres: {genres}")
        print(f"Durasi: {durasi}")
        print(f"ID Song: {id_song}")

        # Insert into KONTEN first
        create_konten_query = f"""
        INSERT INTO "MARMUT"."konten" (id, judul, tanggal_rilis, tahun, durasi)
        VALUES ('{id_song}', '{judul_lagu}', CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), {durasi})
        """
        print(f"Executing create_konten_query: {create_konten_query}")
        result = query(create_konten_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Insert into SONG next
        create_song_query = f"""
        INSERT INTO "MARMUT"."song" (id_konten, id_artist, id_album, total_play, total_download)
        VALUES ('{id_song}', '{artist}', '{id_album}', 0, 0)
        """
        print(f"Executing create_song_query: {create_song_query}")
        result = query(create_song_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Insert genres
        for genre in genres:
            create_genre_query = f"""
            INSERT INTO "MARMUT"."genre" (id_konten, genre)
            VALUES ('{id_song}', '{genre}')
            """
            print(f"Executing create_genre_query: {create_genre_query}")
            result = query(create_genre_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Insert songwriters
        for songwriter in songwriters:
            create_songwriter_query = f"""
            INSERT INTO "MARMUT"."songwriter_write_song" (id_songwriter, id_song)
            VALUES ('{songwriter}', '{id_song}')
            """
            print(f"Executing create_songwriter_query: {create_songwriter_query}")
            result = query(create_songwriter_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Update album's song count and duration
        update_album_query = f"""
        UPDATE "MARMUT"."album"
        SET jumlah_lagu = jumlah_lagu + 1, total_durasi = total_durasi + {durasi}
        WHERE id = '{id_album}'
        """
        print(f"Executing update_album_query: {update_album_query}")
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

def list_albums(request):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
        return redirect('main:login')

    albums = query('SELECT * FROM "MARMUT"."album"')
    return render(request, 'list_albums.html', {'albums': albums})

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
def delete_album(request, id_album):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
        return redirect('main:login')

    if request.method == 'POST':
        delete_album_query = f'DELETE FROM "MARMUT"."album" WHERE id = \'{id_album}\''
        result = query(delete_album_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        if 'Label' in request.session.get('roles', []):
            return redirect('merah:label_manage')
        else:
            return redirect('merah:manage_albums')

    album = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_album}\'')
    if not album:
        if 'Label' in request.session.get('roles', []):
            return redirect('merah:label_manage')
        else:
            return redirect('merah:manage_albums')

    return render(request, 'delete_album.html', {'album': album})

@csrf_exempt
def delete_song(request, id_song):
    if not has_role(request, ['Artist', 'Songwriter', 'Label']):
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

        if 'Label' in request.session.get('roles', []):
            return redirect('merah:label_album_detail', id_album=album_id)
        else:
            return redirect('merah:album_detail', id_album=album_id)

    return JsonResponse({'success': 'false', 'message': 'Invalid request method'}, status=400)

def label_album_detail(request, id_album):
    if not has_role(request, ['Label']):
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

    return render(request, 'label_album_detail.html', {
        'album': album,
        'songs': songs_query
    })
