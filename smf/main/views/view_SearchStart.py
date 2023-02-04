from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models.models import Question,Answer,UserProfile




def loadpage(request,userId):
    return render(request,'search_start.html',{"userId":userId})