from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
@csrf_exempt
def index(request):    
    if is_ajax(request):
        response = {}
        return JsonResponse(response)
    else:
        return render(request,"df.html",{})
# Create your views here.