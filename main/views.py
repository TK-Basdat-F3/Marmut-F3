from django.shortcuts import render
def show_main(request):
    context = {
        'class': 'basdat f'
    }

    return render(request, "main.html", context)
# Create your views here.
