from .forms import UserForm,UserProfileForm
from .view_handler_common import is_ajax,GetNotiMessage
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from .models import UserProfile,InvData
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone


import re
import random

class mymate_info:
    def __init__(self,to_pk,date="",time="",msg="",email="",profile_text="",username=""):
        self.to_pk = to_pk
        self.email = email
        self.msg = msg
        self.time = time
        self.date = date
        self.profile_text = profile_text
        self.username = username

from django.core.mail import send_mail

def handle_mymates(request):
    if is_ajax(request):
        cmd = request.POST.get('cmd')
        data = {}
        mp_pk = UserProfile.objects.filter(user=request.user).first().pk

        if cmd == 'cancel':
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=mp_pk,to_pk=to_pk,accepted=False).first()
            if inv:
                inv.delete()
        elif cmd == 'accept':            
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=to_pk,to_pk=mp_pk,accepted=False).first()
            mp = UserProfile.objects.filter(user=request.user).first()
            tp = UserProfile.objects.filter(pk=to_pk).first()

            if inv:
                inv.accepted = True
                body = "Congratulations! your request has been accepted by the other user. \n\n\
Message:{}\n\
Please visit our webiste and check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format( inv.message if len(inv.message) > 0 else "No Message Attached.")
                send_mail('[SMF] Your request has been accepted.',body, 'SMF Notification<2572258p@gmail.com>', [tp.email])

                inv.date = timezone.localtime(timezone.now()).date()
                inv.time = time=timezone.localtime(timezone.now()).time()
                inv.save()
                
            
        elif cmd == 'reject':
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=to_pk,to_pk=mp_pk,accepted=False).first()
            if inv:
                inv.delete()
        elif cmd == 'disconnect':
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=mp_pk,to_pk=to_pk,accepted=True) | InvData.objects.filter(from_pk=to_pk,to_pk=mp_pk,accepted=True)
            inv.delete()
        return JsonResponse(data)
    else:
        context = {}
        mp = UserProfile.objects.filter(user=request.user).first()
        sent_data = InvData.objects.filter(from_pk=mp.pk,accepted=False)
        rev_data = InvData.objects.filter(to_pk=mp.pk,accepted=False)
        acc_data = InvData.objects.filter(from_pk=mp.pk,accepted=True) | InvData.objects.filter(to_pk=mp.pk,accepted=True)
        context['sent'] = []
        context['rev']  = []
        context['acc']  = []

        for sd in sent_data:
            context['sent'].append(mymate_info(date=str(sd.date),time=sd.time.strftime('%I:%H %p'),to_pk=sd.to_pk,msg=sd.message))
        for rv in rev_data:
            context['rev'].append(mymate_info(date=str(rv.date),time=rv.time.strftime('%I:%H %p'),to_pk=rv.from_pk,msg=rv.message))
        for ac in acc_data:
            connected_pk = ac.to_pk if ac.from_pk == mp.pk else ac.from_pk
            up = UserProfile.objects.filter(pk=connected_pk).first()
            context['acc'].append(mymate_info(date=str(ac.date),time=ac.time.strftime('%I:%H %p'),to_pk=connected_pk,msg=ac.message,email=up.email,profile_text=up.profile_text))

        if mp.has_request == True:
            mp.has_request = False
            mp.save()

        return render(request, 'my_mates.html',context)

def handle_myaccount(request):    
    if is_ajax(request): #Received
        response = {} 
        pf = UserProfile.objects.filter(user=request.user).first()
        if pf:            
            pf.email = request.POST.get('email')
            pf.profile_text = request.POST.get('pf_text')
            pf.profile_text_open = request.POST.get('pf_text_open') == 'true'
            pf.save()
        response['msg'] = "updated"

        return JsonResponse(response)
    else:
        context = {}
        context['username'] = request.user.username
        pf = UserProfile.objects.filter(user=request.user).first()
        if pf:
            context['email'] = pf.email
            context['pf_text'] = pf.profile_text
            context['pf_text_open'] = 'True' if pf.profile_text_open == True else 'False'
            
        return render(request,'profile_management.html',context )


def handle_registration(request):

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
            email=request.POST.get('email'))
            userpf.save()
            
            user = authenticate(username=new_username,password=password)
            if user and user.is_active:
                login(request,user)

        return JsonResponse(response)
    elif is_ajax(request) and request.POST.get('cmd') == 'test_user_fill':

        profile_auto_texts = ['I want to study with you','I love talking wit others','I want to be a friend of yours.']

        user_count = User.objects.all().count()
        response['test_user_name'] = 'user' + str(user_count)
        response['pw'] = '123456ab!'
        response['pw_confirm'] = '123456ab!'
        response['email'] = '2572258p@gmail.com'
        response['pf_text'] = profile_auto_texts[random.randint(0,len(profile_auto_texts)-1)]
        return JsonResponse(response)
    else:        
        return render(request,'profile_registration.html',{} )