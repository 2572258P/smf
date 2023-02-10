from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse



def loadpage(request):
    request.session['temp_session'] = 1    
    return redirect(reverse('main:result'))

    #return render(request,'process_common_loading.html',{})
