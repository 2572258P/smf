from django.http import HttpResponse

def GetWeightByPriority(priority):
    if priority == 'high':
        return 1
    if priority == 'medium':
        return 0.66
    if priority == 'low':
        return 0.33
    return 1
    
def CheckAuth(request):
    if request is None or request.user.is_authenticated is False:
        return False        
    return True

def ShowNotAuthedPage():
    return HttpResponse("This page requires login")

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'