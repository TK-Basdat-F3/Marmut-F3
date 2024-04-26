from django.shortcuts import render

# Create your views here.
def subscribe_menu(request):
    return render(request, "subscribe.html")

def subscribe_form(request):
    return render(request, "subscribe_form.html")

def subscribe_history(request):
    return render(request, "subscribe_history.html")