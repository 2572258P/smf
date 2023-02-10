from django.http import HttpResponse,JsonResponse
from django.shortcuts import render

def loadpage(request):
    print(request.session['temp_session'])
    return render(request,'process_common_result.html',{})