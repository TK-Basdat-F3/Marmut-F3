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

# @login_required
def chart_list(request):

    charts = query('SELECT * FROM "MARMUT"."chart"')
    return render(request, 'chart_list.html', {'charts': charts})

def query(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def chart_detail(request, id_chart, nama_chart):
    try:
        chart_query = query('SELECT * FROM "MARMUT"."chart" WHERE id_playlist = %s', [id_chart])
        if not chart_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        chart = chart_query[0]

        songs_query = query('''
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
        podcast_query = query('SELECT * FROM "MARMUT"."podcast" WHERE id_konten = %s', [id_podcast])
        if not podcast_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        podcast = podcast_query[0]

        detail_query = query('''
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

        episode_query = query('''
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


def kelola_podcast(request):
    try:
        email =  request.session['email']
        podcaster_query = query('SELECT * FROM "MARMUT"."podcaster" WHERE email = %s', [email])
        if not podcaster_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        podcaster = podcaster_query[0]

        podcast_query = query('''
            SELECT 
                podcast.id_konten,
                konten.judul,  
                konten.durasi
            FROM "MARMUT"."podcast"
            JOIN "MARMUT"."konten" ON podcast.id_konten = konten.id     
            JOIN "MARMUT"."akun" ON podcast.email_podcaster = akun.email
            WHERE podcast.email_podcaster = %s
        ''', [email])

        podcast = podcast_query[0] if podcaster_query else None

        return render(request, 'kelola_podcast.html', {
            'podcasts': podcast,
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)

@csrf_exempt
def create_podcast(request):
    if not has_role(request, ['Podcaster']):
        return redirect('main:login')

    genres = query('SELECT DISTINCT genre FROM "MARMUT"."genre"')
    if type(genres) != list:
        genres = []

    if request.method == 'POST':
        judul_podcast = request.POST.get('judul_podcast')
        genres = request.POST.getlist('genres')
        id_podcast = str(uuid.uuid4())
        email =  request.session['email']

        # Insert into KONTEN first
        create_konten_query = f"""
        INSERT INTO "MARMUT"."konten" (id, judul, tanggal_rilis, tahun, durasi)
        VALUES ('{id_podcast}', '{judul_podcast}', CURRENT_DATE, EXTRACT(YEAR FROM CURRENT_DATE), {0})
        """
        print(f"Executing create_konten_query: {create_konten_query}")
        results = query(create_konten_query)
        if type(results) != int:
            return JsonResponse({'success': 'false', 'message': str(results)}, status=200)
        
        create_podcast_query = f"""
        INSERT INTO "MARMUT"."podcast" (id_konten, email_podcaster )
        VALUES ('{id_podcast}', '{email}')
        """
        result = query(create_podcast_query)
        if type(result) != int:
            return JsonResponse({'success': 'false', 'message': str(result)}, status=200)
        
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

        return redirect('biru:create_episode', id_podcast=id_podcast)

    
    return render(request, 'create_podcast.html', {'genres': genres})


def daftarEpisode_podcast(request, id_podcast): 
    try:
        podcast_query = query('SELECT * FROM "MARMUT"."podcast" WHERE id_konten = %s', [id_podcast])
        if not podcast_query:
            return JsonResponse({'success': 'false', 'message': 'Chart not found'}, status=404)
        podcast = podcast_query[0]

        detail_query = query('''
            SELECT 
                podcast.id_konten,
                konten.judul
            FROM "MARMUT"."podcast"
            JOIN "MARMUT"."konten" ON podcast.id_konten = konten.id
            WHERE podcast.id_konten = %s
        ''', [id_podcast])

        detail = e[0] if detail_query else None

        episode_query = query('''
            SELECT 
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

def create_episode(request):
    return render(request, "create_episode.html")
