import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from utilities.helper import query

from .forms import SignupFormPengguna, SignupFormLabel
from django.shortcuts import render
from django.db import OperationalError, ProgrammingError, connection

def show_main(request):
    context = {
        'class': 'basdat f',
    }
    return render(request, "main.html", context)

def main_reg(request):
    return render(request, "main_reg.html")

def register_user(request):
    form = SignupFormPengguna()

    if request.method == "POST":
        form = SignupFormPengguna(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form, 'form2':form}
    return render(request, 'register.html', context)

def register_label(request):
    form2 = SignupFormLabel()

    if request.method == "POST":
        form = SignupFormPengguna(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form, 'form2':form2}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(f"Authenticated User: {user}")
        
        if user is not None:
            login(request, user)
            print(f"Logged in User: {user}")
            
            roles = user.get_roles() if isinstance(user, CustomUser) else ['Label']
            print(f"User Roles: {roles}")

            request.session['username'] = user.username
            request.session['premium_status'] = 'Premium' if user.is_staff else 'Free'
            request.session['roles'] = roles

            if 'Label' in roles:
                request.session['name'] = user[1]
                request.session['email'] = user[2]
                request.session['contact'] = user[4]
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
                print(f"Role-specific Session Data: {request.session.items()}")
                return redirect('main:dashboard_user')
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')
    
def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

@login_required
def dashboard_label(request):
    return render(request, 'dashboard_label.html')

@login_required
def dashboard_user(request):
    return render(request, "dashboard_user.html")


def authenticate_akun(username, password):
    result = query(f'SELECT * FROM "MARMUT"."akun" WHERE email = \'{username}\'')
    akun = result[0] if result else None
    
    # Debugging: Print the query result for akun
    print(f"akun query result: {result}")

    if not akun:
        print("User not found in 'akun', checking 'label' table")
        result = query(f'SELECT * FROM "MARMUT"."label" WHERE email = \'{username}\' AND password = \'{password}\'')
        label = result[0] if result else None
        
        # Debugging: Print the query result for label
        print(f"label query result: {result}")

        if label:
            user = label
            role = 'Label'
        else:
            user = None
            role = None
    else:
        if akun[1] == password:  # Assuming the password is at index 1
            user = akun
            role = 'Akun'
        else:
            user = None
            role = None

    if user:
        premium_status = query(f'SELECT * FROM "MARMUT"."premium" WHERE email = \'{username}\'')
        
        # Debugging: Print the premium status
        print(f"premium_status: {premium_status}")

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

        # Debugging: Print the final user, premium status, and roles
        print(f"Authenticated User: {user}, Premium Status: {premium_status}, Roles: {roles}")

        return user, premium_status, roles
    else:
        return None, False, []

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
        songs.append(song_list)
    print("songs by songwriter: ",songs)
    return songs

def get_podcasts_by_podcaster(username):
    podcaster_id = query(f'SELECT email FROM "MARMUT"."podcaster" WHERE email = \'{username}\'')[0][0]
    id_konten_list = query(f'SELECT id_konten FROM "MARMUT"."podcast" WHERE email_podcaster = \'{podcaster_id}\'')
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
        podcasts.append(podcast_list)
    print("podcasts: ", podcasts)
    return podcasts
