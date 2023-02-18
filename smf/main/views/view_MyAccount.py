from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from main.models.models import Question,Answer,UserProfile
from main.views.view_Base import is_ajax


def loadpage(request):
    if is_ajax(request): #Received
        response = {} 
        cmd = request.POST.get('cmd')
        if cmd == 'update':            
            pf = UserProfile.objects.filter(user=request.user).first()
            if pf:            
                pf.email = request.POST.get('email')
                pf.profile_text = request.POST.get('pf_text')
                pf.profile_text_open = request.POST.get('pf_text_open') == 'true'
                pf.subscribe_dq = request.POST.get('pf_subscribe_dq') == 'true'
                pf.save()
            response['msg'] = "updated"
        elif cmd == 'del_account':
            user = User.objects.filter(username = request.user.username).first()            
            acc_msg = request.POST.get('acc_del_msg')
            print(acc_msg)
            if acc_msg == 'Delete':
                logout(request)
                user.delete()
                response['result'] = True
            else:
                response['result'] = False
        return JsonResponse(response)
    else:
        context = {}
        context['username'] = request.user.username
        pf = UserProfile.objects.filter(user=request.user).first()
        if pf:
            context['email'] = pf.email
            context['pf_text'] = pf.profile_text
            context['pf_text_open'] = 'True' if pf.profile_text_open == True else 'False'
            context['pf_subscribe_dq'] = 'True' if pf.subscribe_dq == True else 'False'
            
        return render(request,'profile_management.html',context )