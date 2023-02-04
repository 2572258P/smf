from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models.models import Question,Answer,UserProfile
from main.views.view_Base import is_ajax


def loadpage(request):
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