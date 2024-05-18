from datetime import datetime
import uuid
from django.shortcuts import render
from utilities.helper import query, get_user_type
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from main.views import authenticate_akun
# Create your views here.
def kelola_playlist(request):
    email = request.session.get('email')

    query_get_all_playlist = query(f'''
                        SELECT judul, email_pembuat, jumlah_lagu, total_durasi, id_playlist
                        FROM "MARMUT".USER_PLAYLIST WHERE email_pembuat = '{email}'
                                   ''')

    
    print(query_get_all_playlist)
    if type(query_get_all_playlist) != list:
        query_get_all_playlist = []

    # print(query_get_all_playlist)
    return render(request, "kelola_playlist.html", {'playlists' : query_get_all_playlist})

def playlist_detail(request, id_playlist):
    query_get_detail_playlist = query(f'''
                                    SELECT email_pembuat, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi, id_user_playlist
                                    FROM "MARMUT".USER_PLAYLIST
                                    WHERE id_playlist = '{id_playlist}';
                                      ''')
    
    query_get_playlist_song = query(f'''
                                SELECT KONTEN.judul, KONTEN.tanggal_rilis, KONTEN.tahun, KONTEN.durasi, AKUN.nama AS penyanyi, KONTEN.id
                                FROM "MARMUT".PLAYLIST_SONG
                                JOIN "MARMUT".SONG ON PLAYLIST_SONG.id_song = SONG.id_konten
                                JOIN "MARMUT".KONTEN ON SONG.id_konten = KONTEN.id
                                JOIN "MARMUT".ARTIST ON SONG.id_artist = ARTIST.id
                                JOIN "MARMUT".AKUN ON AKUN.email = ARTIST.email_akun
                                WHERE PLAYLIST_SONG.id_playlist = '{id_playlist}';
                                ''')
    query_get_all_song_name = query(f'''
                                SELECT SONG.id_konten, judul
                                FROM "MARMUT".KONTEN, "MARMUT".SONG
                                WHERE KONTEN.id = SONG.id_konten 
                                    ''')
    
    # print(query_get_all_song_name)
    

    if type(query_get_detail_playlist) != list:
        query_get_detail_playlist = []
    if type(query_get_playlist_song) != list:
        query_get_playlist_song = []

    return render(request, "playlist_detail.html",{'details': query_get_detail_playlist, 'songs' : query_get_playlist_song, 'popupSongs' : query_get_all_song_name, 'playlistId': id_playlist})

def song_detail(request, id_song):
    
    premium = request.session.get('premium_status')

    query_get_song_detail = query(f'''
                                SELECT  konten.judul as judul, album.judul as album, konten.id as id, konten.tanggal_rilis as tanggal_rilis,
                                        konten.tahun as tahun, konten.durasi as durasi, song.total_play as total_play, song.total_download, 
                                        akun.nama 
                                FROM "MARMUT".song JOIN "MARMUT".artist
                                ON song.id_artist = artist.id JOIN "MARMUT".akun 
                                ON artist.email_akun = akun.email JOIN "MARMUT".konten 
                                ON song.id_konten = konten.id JOIN "MARMUT".album 
                                ON song.id_album = album.id
                                WHERE song.id_konten = '{id_song}';
                                ''')
    
    query_get_song_genre = query(f'''
                                SELECT genre 
                                FROM "MARMUT".genre
                                WHERE genre.id_konten = '{id_song}';
                                 ''')
    
    # print(query_get_song_genre)
    query_get_songwriter = query(f'''
                                SELECT akun.nama
                                FROM "MARMUT".akun 
                                WHERE akun.email IN (
                                    SELECT SONGWRITER.email_akun
                                    FROM "MARMUT".SONGWRITER
                                    JOIN "MARMUT".SONGWRITER_WRITE_SONG ON SONGWRITER.id = SONGWRITER_WRITE_SONG.id_songwriter
                                    JOIN "MARMUT".SONG ON SONGWRITER_WRITE_SONG.id_song = '{id_song}')
                                ''')
    
    email = request.session.get('email')
    query_get_all_user_playlist_name = query(f'''
                                SELECT judul, id_playlist
                                FROM "MARMUT".user_playlist 
                                WHERE email_pembuat = '{email}';
                                ''')
    
    print("-----------------------")
    print(query_get_all_user_playlist_name)

    # check list 
    
    isPremium = False
    print(f"==-=-=-=-=-=-==-=-=-= ${premium}")
    if premium == 'Premium' :
        isPremium = True
    return render(request, "song_detail.html", {'details': query_get_song_detail, 'genres':query_get_song_genre,'songwriters':query_get_songwriter,'playlists':query_get_all_user_playlist_name,'id_song':id_song,'isPremium': isPremium})

@csrf_exempt
def add_song(request,id_playlist):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_lagu = data.get('song-dropdown')      
        print(f'============== {id_playlist}')

    print("+++++++++++++++++++++++")
    print(id_playlist)
    print(id_lagu)
    query_add_song = query(f'''
                           INSERT INTO "MARMUT".PLAYLIST_SONG VALUES (
                               '{id_playlist}',
                               '{id_lagu}'
                           );
                           
                           ''')
    
    
    
    print(query_add_song)
    if query_add_song != 1:
        return  JsonResponse({
            'success': False,
            'message': f'Lagu ini sudah ada didalam playlist!'
        })
    else:
        return JsonResponse({
                'success': True,
                'message': f'Lagu berhasil ditambahkan ke playlist!'
            })

@csrf_exempt
def add_song_from_detail(request,id_song):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_playlist = data.get('playlist')        

    print("+++++++++++++++++++++++")
    print(id_playlist)
    print(id_song)
    query_add_song = query(f'''
                           INSERT INTO "MARMUT".PLAYLIST_SONG VALUES (
                               '{id_playlist}',
                               '{id_song}'
                           );
                           
                           ''')
    
    print(query_add_song)
    if query_add_song != 1:
        return  JsonResponse({
            'success': False,
            'message': f'Lagu ini sudah ada didalam playlist!'
        })
    else:
        return JsonResponse({
                'success': True,
                'message': f'Lagu berhasil ditambahkan ke playlist!'
            })

@csrf_exempt
def delete_song(request, id_playlist,id_song):    
   

    query_delete_playlist_song =query(f'''
                           DELETE 
                           FROM "MARMUT".playlist_song
                           WHERE "MARMUT".playlist_song.id_playlist = '{id_playlist}' AND "MARMUT".playlist_song.id_song = '{id_song}';
                           ''')
   
    
    print(query_delete_playlist_song)
    
    return redirect('hijau:playlist_detail', id_playlist = id_playlist)

@csrf_exempt
def download_song(request,id_song):    
   
    email = request.session.get('email')
    query_download_song =query(f'''
                           INSERT INTO "MARMUT".downloaded_song VALUES ('{id_song}', '{email}')
                           ''')
   
    print("_+_+_+_+_++_+_+_+_+_+_+__+")
    print(query_download_song)
    if query_download_song != 1 :
        return JsonResponse({
            'success': False,
            'message': f'Lagu ini sudah diunduh oleh pengguna {email} '
        })
    else:
        return JsonResponse({
                'success': True,
                'message': f'Lagu berhasil diunduh!'
            })
        
    

@csrf_exempt
def add_playlist(request):
    if request.method == 'POST':
        judul_playlist = request.POST.get('judul')    
        deskripsi_playlist =     request.POST.get('deskripsi')  
        id_playlist = str(uuid.uuid4())
        id_user_playlist =str(uuid.uuid4())
        print('========================')
        print(judul_playlist)
        print(deskripsi_playlist)
    print('===========jhbjhbjh')
    query_add_playlist = query(f'''
                           INSERT INTO "MARMUT".PLAYLIST VALUES ('{id_playlist}')
                           ''')
    
    tanggal = datetime.now().strftime("%Y-%m-%d")
    email = request.session.get('email')
    query_add_user_playlist =query(f'''
                           INSERT INTO "MARMUT".USER_PLAYLIST VALUES (
                               '{email}',
                               '{id_user_playlist}',
                               '{judul_playlist}',
                               '{deskripsi_playlist}',
                               '{int(0)}',
                               '{tanggal}',
                               '{id_playlist}',
                               '{int(0)}'
                               );
                           ''')
    
    print(query_add_playlist)
    print(query_add_user_playlist)
    
    return redirect('hijau:kelola_playlist')

@csrf_exempt
def shuffle_play(request, id_user_playlist, id_playlist,email_pembuat):
    current_timestamp = datetime.now()
    formatted_timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    email = request.session.get('email')
    query_insert_akun_play_user_playlist =query(f'''
                                INSERT INTO "MARMUT".akun_play_user_playlist
                                VALUES (
                                    '{email}',
                                    '{id_user_playlist}',
                                    '{email_pembuat}',
                                    '{formatted_timestamp}'
                                )
                           ''')
    
    
    query_get_all_id_song_playlist = query(f'''
                                SELECT id_song
                                FROM "MARMUT".playlist_song
                                WHERE id_playlist = '{id_playlist}'
                                ;
                           ''')
    
    print("++_+_+_+_+++++++++++++++==============")
    
    print(query_get_all_id_song_playlist)
    
    for id_song in query_get_all_id_song_playlist :
        print(id_song.id_song)
        query_insert_akun_play_song = query(f'''
              INSERT INTO "MARMUT".akun_play_song
              VALUES (
                  '{email}',
                  '{id_song.id_song}',
                  '{formatted_timestamp}'
              )
              ''')
        print(query_insert_akun_play_song)

    if query_insert_akun_play_user_playlist == 1 :
        return JsonResponse({
            'success': True,
            'message': f'Berhasil Shuffle Play!'
        })
            
    else:
        JsonResponse({
            'success': False,
            'message': f'Gagal Shuffle Play!'
        })

@csrf_exempt
def edit_playlist(request):
    if request.method == 'POST':
        judul_playlist = request.POST.get('judul')    
        deskripsi_playlist =     request.POST.get('deskripsi')  
        id_playlist = request.POST.get('id-playlist')
        print('========================')
        print(judul_playlist)
        print(deskripsi_playlist)
        print(id_playlist)

    query_update_user_playlist =query(f'''
                           UPDATE "MARMUT".user_playlist
                           SET judul = '{judul_playlist}', deskripsi = '{deskripsi_playlist}'
                           WHERE "MARMUT".user_playlist.id_playlist = '{id_playlist}';
                           ''')
    
    print(query_update_user_playlist)
    
    return redirect('hijau:kelola_playlist')

@csrf_exempt
def delete_playlist(request, id_playlist):

    query_delete_user_playlist =query(f'''
                           DELETE 
                           FROM "MARMUT".user_playlist
                           WHERE "MARMUT".user_playlist.id_playlist = '{id_playlist}';
                           ''')
   
    print(query_delete_user_playlist)
    return redirect('hijau:kelola_playlist')

csrf_exempt
def play_song(request, id_song):
    if request.method == 'POST':
        data = json.loads(request.body)
        playPct = int(data.get('percentage'))
       

        print(f'============== {id_song}')

    if playPct >= 70:
        current_timestamp = datetime.now()
        formatted_timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        email = request.session.get('email')
        query_play_song = query(f'''
                            INSERT INTO "MARMUT".AKUN_PLAY_SONG VALUES (
                                '{email}',
                                '{id_song}',
                                '{formatted_timestamp}'
                            );
                            ''')
        
        if query_play_song == 1:
            return  JsonResponse({
            'success': True,
            'message': f'Data Play Lagu berhasil dimasukkan kedatabase! (> 70)'
        })
    
    else: 
        return  JsonResponse({
            'success': False,
            'message': f'Lagu gagal dimasukkan kedatabase! (< 70)'
        })
    
    
    
    
