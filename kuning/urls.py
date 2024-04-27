from django.urls import path
from kuning.views import subscribe_menu, subscribe_form, subscribe_history

app_name = 'kuning'

urlpatterns = [
    path('subscribe_menu', subscribe_menu, name='subscribe_menu'),
    path('subscribe_form/', subscribe_form, name='subscribe_form'),
    path('subscribe_history/', subscribe_history, name='subscribe_history'),
]