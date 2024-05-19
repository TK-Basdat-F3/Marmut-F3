import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
import psycopg2
from marmut_f3 import settings
from utilities.helper import query
from django.http.response import JsonResponse
from utilities.helper import query
from .forms import SignupFormPengguna, SignupFormLabel
from django.shortcuts import render
from django.db import OperationalError, ProgrammingError, connection
from django.http import HttpResponseNotFound
import uuid
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def show_main(request):
    context = {
        'class': 'basdat f',
    }
    return render(request, "main.html", context)

@csrf_exempt
def main_reg(request):
    return render(request, "main_reg.html")


@csrf_exempt
def registerlabel(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            nama = request.POST.get('nama')
            kontak = request.POST.get('kontak')

            id = str(uuid.uuid4())

            insert_label_query = f"""
            INSERT INTO "MARMUT"."label" (id, email, password, nama, kontak)
            VALUES ('{id}', '{email}', '{password}', '{nama}', '{kontak}')
            """
            print(f"Executing insert_label_query: {insert_label_query}")

            with connection.cursor() as cursor:
                cursor.execute(insert_label_query)

            success_message = "Berhasil mendaftar sebagai Label."
            return render(request, 'login.html')
        else:
            return render(request, 'registerlabel.html')
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)})

@csrf_exempt
def registeruser(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            nama = request.POST.get('nama')
            tempat_lahir = request.POST.get('tempat_lahir')
            kota_asal = request.POST.get('kota_asal')
            tanggal_lahir_str = request.POST.get('tanggal_lahir')
            tanggal_lahir = None
            if tanggal_lahir_str:
                tanggal_lahir = datetime.strptime(tanggal_lahir_str, '%Y-%m-%d').date()
            gender = request.POST.get('gender')

            is_verified = False
            roles = request.POST.getlist('role')

            insert_akun_query = f"""
            INSERT INTO "MARMUT"."akun" (email, password, nama, tempat_lahir, kota_asal, tanggal_lahir, gender, is_verified)
            VALUES ('{email}', '{password}', '{nama}', '{tempat_lahir}', '{kota_asal}', '{tanggal_lahir}', '{gender}', {is_verified})
            """

            with connection.cursor() as cursor:
                cursor.execute(insert_akun_query)

                for role in roles:
                    if role == 'artist':
                        cursor.execute(f"INSERT INTO \"MARMUT\".\"artist\" (id, email_akun) VALUES ('{str(uuid.uuid4())}', '{email}')")
                    elif role == 'songwriter':
                        cursor.execute(f"INSERT INTO \"MARMUT\".\"songwriter\" (id, email_akun) VALUES ('{str(uuid.uuid4())}', '{email}')")
                    elif role == 'podcaster':
                        cursor.execute(f"INSERT INTO \"MARMUT\".\"podcaster\" (email) VALUES ('{email}')")

                if roles:
                    is_verified = True
                    cursor.execute(f"UPDATE \"MARMUT\".\"akun\" SET is_verified = {is_verified} WHERE email = '{email}'")

            return render(request, 'login.html')
        else:
            return render(request, 'registeruser.html')
    except Exception as e:
        return JsonResponse({'success': 'false', 'message': str(e)})
    
def register_user(request):
    form = SignupFormPengguna()
    if request.method == "POST":
        form = SignupFormPengguna(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form': form, 'form2': form}
    return render(request, 'register.html', context)

@csrf_exempt
def register_label(request):
    form2 = SignupFormLabel()
    if request.method == "POST":
        form = SignupFormPengguna(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form': form, 'form2': form2}
    return render(request, 'register.html', context)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user, is_premium, roles = authenticate_akun(username, password)
        if user is not None:
            request.session['username'] = username
            request.session['premium_status'] = 'Premium' if is_premium else 'Free'
            request.session['roles'] = roles

            check_user_subscription_status(username)

            if 'Label' in roles:
                request.session['nama'] = user.nama 
                request.session['email'] = user.email 
                request.session['kontak'] = user.kontak 
                request.session['album'] = get_album_by_label(username)
                return redirect('main:dashboard_label')
            elif 'Akun' in roles:
                request.session['email'] = user.email
                request.session['password'] = user.password
                request.session['nama'] = user.nama
                request.session['tempat_lahir'] = user.tempat_lahir
                tanggal_lahir_str = user.tanggal_lahir
                request.session['tanggal_lahir'] = tanggal_lahir_str.strftime('%d-%m-%Y')
                request.session['is_verified'] = user.is_verified
                request.session['kota_asal'] = user.kota_asal
                request.session['gender'] = "Perempuan" if user.gender == 0 else "Laki-laki"

                request.session['playlists'] = get_user_playlists_by_user(username)

                if 'Artist' in roles:
                    request.session['songs_by_artist'] = get_songs_by_artist(username)
                if 'Songwriter' in roles:
                    request.session['songs_by_songwriter'] = get_songs_by_songwriter(username)
                # elif 'Artist' and 'Songwriter' in roles:
                #     request.session['songs'] = get_songs_by_artist(username) + get_songs_by_songwriter(username)
                if 'Podcaster' in roles:
                    request.session['podcasts'] = get_podcasts_by_podcaster(username)
                return redirect('main:dashboard_user')
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
            error_message = 'Invalid username or password'
            print(error_message)
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

@csrf_exempt
def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

# @login_required
@csrf_exempt
def dashboard_user(request):
    request.session['premium_status'] = request.session.get('premium_status')
    return render(request, "dashboard_user.html")

# @login_required
@csrf_exempt
def dashboard_label(request):
    return render(request, "dashboard_label.html")

@csrf_exempt
def authenticate_akun(username, password):
    result = query(f'SELECT * FROM "MARMUT"."akun" WHERE email = \'{username}\'')
    akun = result[0] if result else None
    
    if not akun:
        print("User not found in 'akun', checking 'label' table")
        result = query(f'SELECT * FROM "MARMUT"."label" WHERE email = \'{username}\' AND password = \'{password}\'')
        label = result[0] if result else None
        if label:
            user = label
            role = 'Label'
        else:
            user = None
            role = None
    else:
        if akun.password == password:
            user = akun
            role = 'Akun'
        else:
            user = None
            role = None

    if user:
        premium_status = query(f'SELECT * FROM "MARMUT"."premium" WHERE email = \'{username}\'')
        
        if premium_status:
            premium_id = premium_status[0]
            expired_premium = query(f'SELECT * FROM "MARMUT"."transaction" WHERE email = \'{username}\' AND timestamp_berakhir < CURRENT_DATE')
            if expired_premium:
                query(f'DELETE FROM "MARMUT"."downloaded_song" WHERE email_downloader = \'{premium_id}\'')
                query(f'DELETE FROM "MARMUT"."premium" WHERE email = \'{premium_id}\'')
        
        roles = []
        if role == 'Akun':
            roles.append('Akun')
            roles += get_roles_by_email(username)
        else:
            roles.append('Label')

        return user, premium_status, roles
    else:
        return None, False, []

@csrf_exempt
def get_roles_by_email(username):
    roles = []
    artist = query(f'SELECT * FROM "MARMUT"."artist" WHERE email_akun = \'{username}\'')
    if artist:
        roles.append('Artist')
    
    songwriter = query(f'SELECT * FROM "MARMUT"."songwriter" WHERE email_akun = \'{username}\'')
    if songwriter:
        roles.append('Songwriter')
    
    podcaster = query(f'SELECT * FROM "MARMUT"."podcaster" WHERE email = \'{username}\'')
    if podcaster:
        roles.append('Podcaster')
    
    return roles

@csrf_exempt
def get_user_playlists_by_user(username):
    playlists = query(f'''
                      SELECT up.judul 
                      FROM "MARMUT"."playlist" p
                      INNER JOIN "MARMUT"."user_playlist" up ON p.id = up.id_playlist
                      WHERE up.email_pembuat = \'{username}\'
                      ''')
    if len(playlists) == 0:
        return playlists
    return playlists[0]

@csrf_exempt
def get_songs_by_artist(username):
    artist_id = query(f'SELECT id FROM "MARMUT"."artist" WHERE email_akun = \'{username}\'')[0][0]
    print("artist_id: ", artist_id)
    songs = query(f'''
                    SELECT k.judul, a.nama, k.durasi
                    FROM "MARMUT"."konten" k
                    INNER JOIN "MARMUT"."song" s ON s.id_konten = k.id
                    JOIN "MARMUT"."artist" art ON s.id_artist = art.id
                    JOIN "MARMUT"."akun" a ON art.email_akun = a.email
                    WHERE s.id_artist = \'{artist_id}\'
                ''')
    print("songs: ", songs)
    return songs

@csrf_exempt
def get_songs_by_songwriter(username):
    songwriter_id = query(f'SELECT id FROM "MARMUT"."songwriter" WHERE email_akun = \'{username}\'')[0][0]
    song_ids = query(f'SELECT id_song FROM "MARMUT"."songwriter_write_song" WHERE id_songwriter = \'{songwriter_id}\'')
    songs = []
    for song_id in song_ids:
        song_list = []
        song = query(f'''
            SELECT k.judul, a.nama, k.durasi
            FROM "MARMUT"."song" s
            INNER JOIN "MARMUT"."konten" k ON s.id_konten = k.id
            JOIN "MARMUT"."artist" art ON s.id_artist = art.id
            JOIN "MARMUT"."akun" a ON art.email_akun = a.email
            WHERE s.id_konten = \'{song_id[0]}\'
        ''')[0]
        song_list.append(song.judul)
        song_list.append(song.nama)
        song_list.append(song.durasi)
        song_list.append(str(song_id[0]))
        songs.append(song_list)
    print("songs by songwriter: ",songs)
    return songs

@csrf_exempt
def get_podcasts_by_podcaster(username):
    podcaster_email = query(f'SELECT email FROM "MARMUT"."podcaster" WHERE email = \'{username}\'')[0][0]
    id_konten_list = query(f'SELECT id_konten FROM "MARMUT"."podcast" WHERE email_podcaster = \'{podcaster_email}\'')
    podcasts = []
    for id_konten in id_konten_list:
        print("id_konten: ",id_konten[0])
        podcast_list = []
        title = query(f'SELECT judul FROM "MARMUT"."konten" WHERE id = \'{id_konten[0]}\'')[0][0]
        total_episodes = query(f'SELECT COUNT(*) as total_episodes FROM "MARMUT"."episode" WHERE id_konten_podcast = \'{id_konten[0]}\'')[0][0]
        total_durasi = query(f'SELECT SUM(durasi) as total_durasi FROM "MARMUT"."episode" WHERE id_konten_podcast = \'{id_konten[0]}\'')[0][0]
        podcast_list.append(title)
        podcast_list.append(total_episodes)
        podcast_list.append(total_durasi)
        podcast_list.append(str(id_konten[0]))
        podcasts.append(podcast_list)
    print("podcasts: ", podcasts)
    return podcasts

@csrf_exempt
def get_album_by_label(username):
    label_id = query(f'SELECT id FROM "MARMUT"."label" WHERE email = \'{username}\'')[0][0]
    id_album_list = query(f'SELECT id FROM "MARMUT"."album" WHERE id_label = \'{label_id}\'')
    albums = []
    for id_album in id_album_list:
        print("id_album: ",id_album[0])
        album_list = []
        title = query(f'SELECT judul FROM "MARMUT"."album" WHERE id = \'{id_album[0]}\'')[0][0]
        total_lagu = query(f'SELECT jumlah_lagu FROM "MARMUT"."album" WHERE id = \'{id_album[0]}\'')[0][0]
        total_durasi = query(f'SELECT total_durasi FROM "MARMUT"."album" WHERE id = \'{id_album[0]}\'')[0][0]
        album_list.append(title)
        album_list.append(total_lagu)
        album_list.append(total_durasi)
        album_list.append(str(id_album[0]))
        albums.append(album_list)
    print("albums: ", albums)
    return albums

@csrf_exempt
def check_user_subscription_status(user_email):
    connection = None
    try:
        # Connect to your PostgreSQL database
        connection = psycopg2.connect(
            dbname="your_dbname",
            user="your_username",
            password="your_password",
            host="your_host",
            port="your_port"
        )
        
        cursor = connection.cursor()
        
        # Call the stored procedure
        cursor.execute("CALL check_and_update_subscription_status(%s)", (user_email,))
        
        # Commit the transaction
        connection.commit()
        
        print(f"Checked and updated subscription status for {user_email}")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
