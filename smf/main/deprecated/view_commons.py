from django.http import HttpResponse
from django.shortcuts import redirect


def GetWeightByPriority(priority):
    if priority == 'high':
        return 1
    if priority == 'medium':
        return 0.66
    if priority == 'low':
        return 0.33
    return 1
    
def GetNotiMessage(msg):
    if len(msg) > 0:
        return msg
    else:
        return "No Message Attached."

def GetCategoryLabel(letters):
    if letters == 'cc':
        return 'Common'
    elif letters == 'cd':
        return 'Details'
    elif letters == 'cb':
        return 'Pychology'

def CheckAuth(request):
    if request is None or request.user.is_authenticated is False:
        return False        
    return True

def ShowNotAuthedPage():
    return redirect('main:page_signin_requirement')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'