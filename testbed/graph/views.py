from django.shortcuts import render


def index(request):
    return render(request,'graph_index.html',{})
# Create your views here.
