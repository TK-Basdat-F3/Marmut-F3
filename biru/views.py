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
            JOIN "MARMUT"."genre" ON podcast.id_konten = genre.id          
            JOIN "MARMUT"."akun" ON podcast.email_podcaster = akun.email
            WHERE podcast.id_konten = %s
        ''', [id_podcast])

        episode_query = query('''
            SELECT 
                episode.judul,
                episode.deskripsi,
                episode.durasi,
                episode.tanggal            
            FROM "MARMUT"."episode"
            WHERE episode.id_konten_podcast = %s
        ''', [id_podcast])

        return render(request, 'play_podcast.html',{
            'podcast': podcast,
            'detail': detail_query,
            'episodes' : episode_query
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)


def kelola_podcast(request):
    try:
        # songs_query = query('''
        #     SELECT 
        #         song.id_konten,
        #         konten.judul,  
        #         akun.nama,
        #         konten.tanggal_rilis,
        #         song.total_play 
        #     FROM "MARMUT"."playlist_song"
        #     JOIN "MARMUT"."song" ON song.id_konten = playlist_song.id_song
        #     JOIN "MARMUT"."konten" ON song.id_konten = konten.id
        #     JOIN "MARMUT"."artist" ON song.id_artist = artist.id
        #     JOIN "MARMUT"."akun" ON artist.email_akun = akun.email
        #     WHERE playlist_song.id_playlist = %s
        # ''', ["8"])

        return render(request, 'kelola_podcast.html', {
            # 'songs': songs_query,
        })
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)}, status=500)

@csrf_exempt
def create_podcast(request):
    # if not has_role(request, ['Podcaster']):
    #     return redirect('main:login')

    # if request.method == 'POST':
    #     judul_podcast = request.POST.get('judul_podcast')
    #     genre = request.POST.get('genre')
    #     podcaster = request.POST.get('podcaster')
    #     id_podcast = str(uuid.uuid4())

    #     create_podcast_query = f"""
    #     INSERT INTO "MARMUT"."podcast" (id_email, )
    #     VALUES ('{id_album}', '{judul_album}', 0, '{label}', 0)
    #     """
    #     result = query(create_podcast_query)
    #     if type(result) != int:
    #         return JsonResponse({'success': 'false', 'message': str(result)}, status=200)

    #     return redirect('biru:create_episode', id_podcast=id_podcast)

    # albums = query('SELECT * FROM "MARMUT"."podcast"')
    # if type(podcast) != list:
    #     podcast = []
    return render(request, 'kelola_podcast.html', {'podcast': podcast})


def daftarEpisode_podcast(request):
    return render(request, "daftarEpisode_podcast.html")

def create_episode(request):
    return render(request, "create_episode.html")
