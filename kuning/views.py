from django.db import connection
from django.http import HttpResponseNotFound
from django.shortcuts import render
from psycopg2 import OperationalError, ProgrammingError
from uuid import UUID

# Create your views here.
def subscribe_menu(request):
    return render(request, "subscribe.html")

def subscribe_form(request):
    return render(request, "subscribe_form.html")

def subscribe_history(request):
    return render(request, "subscribe_history.html")

def downloaded_songs(request):
    return render(request, "downloaded_songs.html")

def search_content(request):
    return render(request, "search_content.html")

def search_found(request):
    return render(request, "search_found.html")
