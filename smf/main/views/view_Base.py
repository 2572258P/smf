from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse

from main.models.models import Question,Answer,UserProfile
    
def GetNotiMessage(msg):
    if len(msg) > 0:
        return msg
    else:
        return "No Message Attached."

def CheckAuth(request):
    if request is None or request.user.is_authenticated is False:
        return False 
    return True

def ShowNotAuthedPage():
    return redirect(reverse('main:page_signin_requirement'))


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def signout(request):
    logout(request)
    return redirect(reverse('main:home'))

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                #Attempt login
                login(request,user)                

                #Delete invalid answers
                mup = UserProfile.objects.filter(user=user).first()
                if mup:
                    anss = Answer.objects.filter(profile=mup)                    
                    for ans in anss:                        
                        if not Question.objects.filter(pk=ans.question_id).first():
                            print("deleted:",ans.pk)
                            ans.delete()


                return redirect(reverse('main:home'))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            HttpResponse(f"Invalid login details: {username},{password}")
            return HttpResponse("Invalid login details supplied.")

    return HttpResponse("The request was not POST type")