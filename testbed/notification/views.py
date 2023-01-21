from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    if request.method == 'POST':
        print("hahaha")
    
    return render(request,"noti.html",{})
# Create your views here.
