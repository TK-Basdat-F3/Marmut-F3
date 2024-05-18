import datetime
from dateutil.relativedelta import relativedelta
from django.db import connection
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from psycopg2 import OperationalError, ProgrammingError
from uuid import uuid4
from marmut_f3 import settings
from utilities.helper import query
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def subscribe_menu(request):
    username = request.session.get('username')

    if not username:
        return HttpResponseNotFound("User not logged in.")
    
    paket = query(f'SELECT jenis, harga FROM "MARMUT"."paket"')
    request.session['paket'] = paket
    return render(request, "subscribe.html")

def subscribe_form(request, id):
    username = request.session.get('username')

    if not username:
        return HttpResponseNotFound("User not logged in.")
    
    paket = query(f'SELECT jenis, harga FROM "MARMUT"."paket"')
    request.session['paket_selected'] = paket[id]
    request.session['metode_pembayaran'] = ["Transfer bank", "Kartu kredit", "E-Wallet"]
    return render(request, "subscribe_form.html")

@csrf_exempt
def add_transaction(request):
    username = request.session.get('username')
    if not username:
        return HttpResponseNotFound("User not logged in.")
    
    if request.method == 'POST':
        metode_bayar = request.POST.get('payment_method')

    current_date = datetime.datetime.now()
    active_subscription = query(f'''
                                SELECT id FROM "MARMUT"."transaction"
                                WHERE email = \'{username}\' AND timestamp_berakhir > \'{current_date}\'
                                ''')

    if active_subscription:
        return JsonResponse({'error': 'There is already an active subscription.'}, status=400)
    
    paket_selected = request.session.get('paket_selected')
    transaction_id = str(uuid4())

    if paket_selected[0] == "1 Bulan":
        timestamp_berakhir = current_date + relativedelta(months=1)
    elif paket_selected[0] == "3 Bulan":
        timestamp_berakhir = current_date + relativedelta(months=3)
    elif paket_selected[0] == "6 Bulan":
        timestamp_berakhir = current_date + relativedelta(months=6)
    elif paket_selected[0] == "1 Tahun":
        timestamp_berakhir = current_date + relativedelta(years=1)
    
    timestamp_dimulai_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_berakhir_str = timestamp_berakhir.strftime('%Y-%m-%d %H:%M:%S')
        
    transaction = query(f'''
                        INSERT INTO "MARMUT"."transaction"
                        (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal) 
                        VALUES
                        (\'{transaction_id}\', \'{paket_selected[0]}\', \'{username}\', \'{timestamp_dimulai_str}\', \'{timestamp_berakhir_str}\', \'{metode_bayar}\', \'{paket_selected[1]}\')
                        ''')  
    if type(transaction) != int:
        return JsonResponse({'success': 'false', 'message': str(transaction)}, status=200)
    
    premium_status = request.session.get('premium_status')
    if premium_status == 'Free':
        premium = query(f'INSERT INTO "MARMUT"."premium" (email) VALUES (\'{username}\')')
        if type(premium) != int:
            return JsonResponse({'success': 'false', 'message': str(premium)}, status=200)
        
        remove_nonpremium = query(f'DELETE FROM "MARMUT"."nonpremium" WHERE email = \'{username}\'')
        if type(remove_nonpremium) != int:
            return JsonResponse({'success': 'false', 'message': str(remove_nonpremium)}, status=200)

    request.session['premium_status'] = "Premium"

    return redirect('kuning:subscribe_history')

def subscribe_history(request):
    username = request.session.get('username')

    if not username:
        return HttpResponseNotFound("User not logged in.")
    
    email = query(f'SELECT email FROM "MARMUT"."transaction" WHERE email = \'{username}\'')
    transaction = []

    if email:
        trans_ids = query(f'SELECT id FROM "MARMUT"."transaction" WHERE email = \'{email[0][0]}\'')
        for trans_id in trans_ids:
            trans_list = []
            trans = query(f'''
                          SELECT t.jenis_paket, t.timestamp_dimulai, t.timestamp_berakhir, t.metode_bayar, t.nominal
                          FROM "MARMUT"."transaction" t
                          WHERE t.id = \'{trans_id[0]}\'
                          ''')[0]
            print(trans)
            trans_list.append(trans.jenis_paket)
            trans_list.append(str(trans.timestamp_dimulai))
            trans_list.append(str(trans.timestamp_berakhir))
            trans_list.append(trans.metode_bayar)
            trans_list.append(trans.nominal)
            transaction.append(trans_list)
    request.session['subscribe_history'] = transaction
    return render(request, "subscribe_history.html")

def downloaded_songs(request):
    username = request.session.get('username')

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
