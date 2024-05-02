
from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('main/', views.show_main, name='show_main'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard_user/', views.dashboard_user, name='dashboard_user'),
    path('dashboard_label/', views.dashboard_label, name='dashboard_label'),
    path('main_reg/', views.main_reg, name='main_reg'),
]