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
from uuid import UUID

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
        user, is_premium, roles = authenticate_akun(username, password)
        if user is not None:
            request.session['username'] = username
            request.session['premium_status'] = 'Premium' if is_premium else 'Free'
            request.session['roles'] = roles

            if 'Label' in roles:
                request.session['name'] = user[1]
                request.session['email'] = user[2]
                request.session['contact'] = user[4]
                return redirect('main:dashboard_label')
            elif 'Akun' in roles:
                # Mengonversi user ke dalam dictionary
                user_data = {
                    'email': user.email,
                    'password': user.password,
                    'nama': user.nama,
                    'tempat_lahir': user.tempat_lahir,
                    'tanggal_lahir': user.tanggal_lahir,
                    'is_verified': user.is_verified,
                    'kota_asal': user.kota_asal,
                    'gender': "Perempuan" if user.gender == 0 else "Laki-laki",
                }

                # Mengonversi data ke dalam JSON
                user_json = json.dumps(user_data, cls=DjangoJSONEncoder)

                # Menyimpan data ke dalam sesi
                request.session['user_data'] = user_json
                if 'Artist' in roles:
                    request.session['songs'] = get_songs_by_artist(username)
                elif 'Songwriter' in roles:
                    request.session['songs'] = get_songs_by_songwriter(username)
                elif 'Artist' and 'Songwriter' in roles:
                    request.session['songs'] = get_songs_by_artist(username) + get_songs_by_songwriter(username)
                elif 'Podcaster' in roles:
                    request.session['podcasts'] = get_podcasts_by_podcaster(username)
                return redirect('main:dashboard_user')
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
            error_message = 'Invalid username or password'
            print(error_message)
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

# @login_required
def dashboard_user(request):
    return render(request, "dashboard_user.html")

# @login_required
def dashboard_label(request):
    return render(request, "dashboard_label.html")


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

def get_songs_by_artist(username):
    artist_id = query(f'SELECT id FROM "MARMUT"."artist" WHERE email_akun = \'{username}\'')[0]
    songs = query(f'''
        SELECT k.judul
        FROM "MARMUT"."song" s
        INNER JOIN "MARMUT"."konten" k ON s.id_konten = k.id
        WHERE s.id_artist = \'{artist_id}
    ''')
    return [song.judul for song in songs]

def get_songs_by_songwriter(username):
    songwriter_id = query(f'SELECT id FROM "MARMUT"."songwriter" WHERE email_akun = \'{username}\'')[0]
    song_ids = query(f'SELECT id_song FROM "MARMUT"."songwriter_write_song" WHERE id_songwriter = \'{songwriter_id}\'')
    song_titles = []
    for song_id in song_ids:
        song_title = query(f'''
            SELECT k.judul
            FROM "MARMUT"."song" s
            INNER JOIN "MARMUT"."konten" k ON s.id_konten = k.id
            WHERE s.id_konten = \'{song_id}\'
        ''')[0]
        song_titles.append(song_title.judul)
    return song_titles

def get_podcasts_by_podcaster(username):
    podcaster_id = query(f'SELECT email FROM "MARMUT"."podcaster" WHERE email = \'{username}\'')[0]
    id_konten_list = query(f'SELECT id_konten FROM "MARMUT"."podcast" WHERE email_podcaster = \'{podcaster_id}\'')
    podcast_titles = []
    for id_konten in id_konten_list:
        title = query(f'SELECT judul FROM "MARMUT"."konten" WHERE id = \'{id_konten}\'')[0]
        podcast_titles.append(title.judul)
    return podcast_titles