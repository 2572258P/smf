from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    if request.method == 'POST':
        send_mail('A cool subject', 'A stunning message', settings.EMAIL_HOST_USER, ['midwayspark@gmail.com'])
    return render(request,"noti.html",{})
# Create your views here.
