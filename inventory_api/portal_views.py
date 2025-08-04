from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def login_view(request):
    return render(request, 'portal/login.html')

def home_view(request):
    return render(request, 'portal/home.html')
