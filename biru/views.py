from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from utilities.helper import query, get_user_type
from django.http.response import JsonResponse
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection

def has_role(request, required_roles):
    user_roles = request.session.get('roles', [])
    return any(role in user_roles for role in required_roles)

def querys(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
# @login_required
def chart_list(request):
    charts = querys('SELECT * FROM "MARMUT"."chart"')
    return render(request, 'chart_list.html', {'charts': charts})

def chart_detail(request, id_chart, nama_chart):
    try:
        chart_query = querys('SELECT * FROM "MARMUT"."chart" WHERE id_playlist = %s', [id_chart])
        if not chart_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        chart = chart_query[0]

        songs_query = querys('''
            SELECT 
                song.id_konten,
                konten.judul,  
                akun.nama,
                konten.tanggal_rilis,
                song.total_play 
            FROM "MARMUT"."playlist_song"
            JOIN "MARMUT"."song" ON song.id_konten = playlist_song.id_song
            JOIN "MARMUT"."konten" ON song.id_konten = konten.id
            JOIN "MARMUT"."artist" ON song.id_artist = artist.id
            JOIN "MARMUT"."akun" ON artist.email_akun = akun.email
            WHERE playlist_song.id_playlist = %s
        ''', [id_chart])

        return render(request, 'chart_detail.html', {
            'chart': chart,
            'songs': songs_query,
            'nama_chart' : nama_chart
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)

def play_podcast(request, id_podcast):
    try:
        podcast_query = querys('SELECT * FROM "MARMUT"."podcast" WHERE id_konten = %s', [id_podcast])
        if not podcast_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        podcast = podcast_query[0]

        detail_query = querys('''
            SELECT 
                podcast.id_konten,
                konten.judul,  
                genre.genre,
                akun.nama,
                konten.durasi,
                konten.tanggal_rilis,
                konten.tahun
            FROM "MARMUT"."podcast"
            JOIN "MARMUT"."konten" ON podcast.id_konten = konten.id
            JOIN "MARMUT"."genre" ON podcast.id_konten = genre.id_konten          
            JOIN "MARMUT"."akun" ON podcast.email_podcaster = akun.email
            WHERE podcast.id_konten = %s
        ''', [id_podcast])

        detail = detail_query[0] if detail_query else None

        episode_query = querys('''
            SELECT 
                episode.judul,
                episode.deskripsi,
                episode.durasi,
                episode.tanggal_rilis            
            FROM "MARMUT"."episode"
            WHERE episode.id_konten_podcast = %s
        ''', [id_podcast])

        return render(request, 'play_podcast.html',{
            'podcast': podcast,
            'detail': detail,
            'episodes' : episode_query
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)

from django.shortcuts import render
from django.http import JsonResponse

def kelola_podcast(request):
    try:
        email = request.session.get('email')
        if not email:
            return JsonResponse({'success': 'false', 'message': 'User not logged in'}, status=403)
        
        podcaster_query = querys('SELECT * FROM "MARMUT"."podcaster" WHERE email = %s', [email])
        if not podcaster_query:
            return JsonResponse({'success': 'false', 'message': 'Podcaster not found'}, status=404)
        
        podcaster = podcaster_query[0]

        podcast_query = querys('''
            SELECT 
                podcast.id_konten,
                konten.judul,  
                konten.durasi,
                COUNT(episode.id_episode) as jumlah_episode,
                SUM(episode.durasi) as total_durasi
            FROM "MARMUT"."podcast"
            JOIN "MARMUT"."konten" ON podcast.id_konten = konten.id     
            LEFT JOIN "MARMUT"."episode" ON episode.id_konten_podcast = podcast.id_konten
            WHERE podcast.email_podcaster = %s
            GROUP BY podcast.id_konten, konten.judul, konten.durasi
        ''', [email])
        
        podcasts = podcast_query if podcast_query else []
        if type(podcasts) != list:
            podcasts = []

        return render(request, 'kelola_podcast.html', {
            'podcasts': podcasts,
            'poo': podcaster,
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)


from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import uuid

@csrf_exempt
def create_podcast(request):
    try:
        if request.method == 'POST':
            email = request.session.get('email')
            if not email:
                return JsonResponse({'success': 'false', 'message': 'User not authenticated'}, status=403)

            judul = request.POST.get('judul')
            genres = request.POST.getlist('genres')
            id_podcast = str(uuid.uuid4())

            # Insert into KONTEN first
            create_konten_query = f"""
            INSERT INTO "MARMUT"."konten" (id, judul, tanggal_rilis, tahun, durasi)
            VALUES ('{id_podcast}', '{judul}', CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), {0})
            """
            print(f"Executing create_konten_query: {create_konten_query}")
            result = query(create_konten_query)
            if type(result) != int:
                return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
            
            # Insert into PODCAST
            create_podcast_query = f"""
            INSERT INTO "MARMUT"."podcast" (id_konten, email_podcaster)
            VALUES ('{id_podcast}', '{email}')
            """
            podcast_results = query(create_podcast_query)
            if podcast_results is None:
                return JsonResponse({'success': 'false', 'message': 'Error creating podcast'}, status=500)

            # Insert genres
            for genre in genres:
                create_genre_query = f"""
                INSERT INTO "MARMUT"."genre" (id_konten, genre)
                VALUES ('{id_podcast}', '{genre}')
                """
                print(f"Executing create_genre_query: {create_genre_query}")
                result = query(create_genre_query)
                if type(result) != int:
                    return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
                
             # Redirect to 'biru:kelola_podcast' after successful form submission
            return redirect('biru:kelola_podcast')

        genres = query('SELECT DISTINCT genre FROM "MARMUT"."genre"')
        if type(genres) != list:
            genres = []

        return render(request, 'create_podcast.html',{
            'genres' : genres
        })

    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)


def delete_podcast(request, id_podcast):
    if not has_role(request, ['Podcaster']):
        return redirect('main:login')

    if request.method == 'POST':
        delete_podcast_query = f'DELETE FROM "MARMUT"."podcast" WHERE id_konten = \'{id_podcast}\''
        result = query(delete_podcast_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        return redirect('biru:kelola_podcast')

    podcast = query(f'SELECT * FROM "MARMUT"."album" WHERE id = \'{id_podcast}\'')
    if not podcast:
        return redirect('biru:kelola_podcast')

    return render(request, 'delete_album.html', {'podcast': podcast})

def daftar_episode(request, id_podcast): 
    try:
        podcast_query = querys('SELECT * FROM "MARMUT"."podcast" WHERE id_konten = %s', [id_podcast])
        if not podcast_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        podcast = podcast_query[0]

        detail_query = querys('''
            SELECT 
                podcast.id_konten,
                konten.judul
            FROM "MARMUT"."podcast"
            JOIN "MARMUT"."konten" ON podcast.id_konten = konten.id
            WHERE podcast.id_konten = %s
        ''', [id_podcast])

        detail = detail_query[0] if detail_query else None

        episode_query = querys('''
            SELECT 
                episode.id_episode,
                episode.judul,
                episode.deskripsi,
                episode.durasi,
                episode.tanggal_rilis            
            FROM "MARMUT"."episode"
            WHERE episode.id_konten_podcast = %s
        ''', [id_podcast])

        return render(request, 'daftarEpisode_podcast.html',{
            'podcast': podcast,
            'detail': detail,
            'episodes' : episode_query
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)
  
@csrf_exempt
def delete_episode(request, id_podcast):
    if not has_role(request, ['Podcaster']):
        return redirect('main:login')

    if request.method == 'POST':
        episode_id = request.POST.get('id_episode')
        print(episode_id+"ugdigdyuegf")

        delete_episode_query = f'DELETE FROM "MARMUT"."episode" WHERE id_episode = \'{episode_id}\''
        result = query(delete_episode_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

        # Redirect to the episode list page after successful deletion
        return redirect('biru:daftar_episode', id_podcast=id_podcast)

    return JsonResponse({'success': 'false', 'message': 'Invalid request method'}, status=400)   

@csrf_exempt
def create_episode(request, id_podcast):
    try:
        podcast_query = query(f'SELECT * FROM "MARMUT"."podcast" WHERE id_konten = \'{id_podcast}\'')
        if podcast_query is None or len(podcast_query) == 0:
            return JsonResponse({'success': 'false', 'message': 'Podcast not found'}, status=404)
        podcast = podcast_query[0]

        if request.method == 'POST':
            judul = request.POST.get('judul')
            deskripsi = request.POST.get('deskripsi')
            durasi = request.POST.get('durasi')
            if not judul or not deskripsi or not durasi:
                return JsonResponse({'success': 'false', 'message': 'Missing required fields'}, status=400)

            id_episode = str(uuid.uuid4())

            # Insert into EPISODE
            create_episode_query = f"""
            INSERT INTO "MARMUT"."episode" (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
            VALUES ('{id_episode}', '{id_podcast}', '{judul}', '{deskripsi}', '{durasi}', CURRENT_DATE)
            """
            results = query(create_episode_query)
            if isinstance(results, Exception) or results != 1:
                return JsonResponse({'success': 'false', 'message': 'Error creating episode'}, status=500)
            
            # Redirect to 'biru:kelola_podcast' after successful form submission
            return redirect('biru:kelola_podcast')

        return render(request, 'create_episode.html', {
            'podcast': podcast,
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)