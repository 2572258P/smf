from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models.models import Question,Answer,UserProfile


def loadpage(request):
    return render(request,'sign_in_requirement.html',{})