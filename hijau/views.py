from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from utilities.helper import query
import datetime

# Create your views here.
def kelola_playlist(request):
    return render(request, "kelola_playlist.html")

def detail_playlist(request):
    return render(request, "detail_playlist.html")

def detail_song(request):
    return render(request, "detail_song.html")

def play_user_playlist(request, id_user_playlist, id_song):
    username = request.session.get('username')
    if not username:
        return HttpResponseNotFound("User not logged in.")
    
    email_pembuat_result = query(f'SELECT email_pembuat FROM "MARMUT"."user_playlist" WHERE id_user_playlist = \'{id_user_playlist}\'')
    if not email_pembuat_result:
        return JsonResponse({'success': 'false', 'message': 'Playlist not found or user is not the creator'}, status=404)

    email_pembuat = email_pembuat_result[0]['email_pembuat']
    
    current_date = datetime.datetime.now()
    akun_play_up = query(f'''
                         INSERT INTO "MARMUT"."akun_play_user_playlist"
                         (email_pemain, id_user_playlist, email_pembuat, waktu)
                         VALUES
                         (\'{username}\', \'{id_user_playlist}\', \'{email_pembuat}\', \'{current_date}\')
                         ''')
    if type(akun_play_up) != int:
        return JsonResponse({'success': 'false', 'message': str(akun_play_up)}, status=200)
    
    akun_play_song = query(f'''
                         INSERT INTO "MARMUT"."akun_play_song"
                         (email_pemain, id_song, waktu)
                         VALUES
                         (\'{username}\', \'{id_song}\', \'{current_date}\')
                         ''')
    if type(akun_play_song) != int:
        return JsonResponse({'success': 'false', 'message': str(akun_play_song)}, status=200)

    return JsonResponse({'success': 'true', 'message': 'Playlist and song play logged successfully'}, status=200)
