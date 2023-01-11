from django.shortcuts import render
from django.http import JsonResponse

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def index(request):
    if request.method == "GET":
        return render(request, 'index.html')
    elif is_ajax(request):
        data = request.POST.get('text', None)
        if data:
            response = { 'msg': data,'dt' : '1' }
            return JsonResponse(response)
        else:
            response = { 'msg': "" }
            return JsonResponse(response)

