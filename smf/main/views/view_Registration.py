from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login

from main.models.models import Question,Answer,UserProfile
from .view_Base import is_ajax
import random
import re

def loadpage(request):
    response = {}
    if is_ajax(request) and request.POST.get('cmd') == 'create':        
        check_username = request.POST.get('check_username')        
        new_username = request.POST.get('username')
        password = request.POST.get('password')        
        success = False

        if new_username is not None and len(new_username) < 5:
            response['msg'] = "User name must be at least five letters."
        elif new_username is not None and re.match("^[A-Za-z0-9_-]*$",new_username) == None:
            response['msg'] = "Special letters are not allowed to use for user name."
        elif User.objects.filter(username = new_username).first():
            response['msg'] = "User name \"{}\" is not available.".format(new_username)
        elif password is not None and len(password) < 8:
            response['msg'] = "Password must to be set eight letters at least."
        else:
            success = True
        response['success'] = success

        if success:
            newuser = User.objects.create_user(username=new_username, password=password)
            userpf = UserProfile(user=newuser,
            profile_text=request.POST.get('pf_text'),
            profile_text_open=request.POST.get('pf_text_open') == 'true',
            subscribe_dq=request.POST.get('pf_subscribe_dq') == 'true',
            email=request.POST.get('email'))
            userpf.save()
            
            user = authenticate(username=new_username,password=password)
            if user and user.is_active:
                login(request,user)

        return JsonResponse(response)
    elif is_ajax(request) and request.POST.get('cmd') == 'test_user_fill':

        profile_auto_texts = ['I want to study with you','I love talking with others','I want to be a friend of yours.']

        user_count = User.objects.all().count()
        response['test_user_name'] = 'user' + str(user_count)
        response['pw'] = '123456ab!'
        response['pw_confirm'] = '123456ab!'
        response['email'] = '2572258p@gmail.com'
        response['pf_text'] = profile_auto_texts[random.randint(0,len(profile_auto_texts)-1)]
        return JsonResponse(response)
    else:        
        return render(request,'profile_registration.html',{} )